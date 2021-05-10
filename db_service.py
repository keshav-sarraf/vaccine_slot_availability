import base64
import datetime
import json
import os
import time
from functools import lru_cache
import cachetools.func

import requests
from firebase_admin import firestore

# Use the application default credentials
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from pytz import timezone

from api_service import get_all_dist_codes_api, get_dist_vaccination_calendar


def _get_firebase_credentials():
    if 'FIREBASE_CONFIG_BASE64' in os.environ:
        # created encoded config and saved in var in heroku
        # openssl base64 -in <firebaseConfig.json> -out <firebaseConfigBase64.txt> -A
        config_json_base64 = os.environ['FIREBASE_CONFIG_BASE64']
        base64_bytes = config_json_base64.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        cred = credentials.Certificate(json.loads(message))
    else:
        cred = credentials.Certificate("vaccineslotavailability-firebase-adminsdk-6jiff-78515b332d.json")

    return cred


firebase_admin.initialize_app(_get_firebase_credentials())
db = firestore.client()


def _get_topic_from_dist_id(dist_id):
    return "/topics/{}".format(dist_id)


def _get_slot_document_key(dist_id):
    return "dist_{}".format(dist_id)


@cachetools.func.ttl_cache(maxsize=1, ttl=10 * 60 * 60)
def get_all_dist_codes_db():
    doc_ref = db.collection(u'static').document(u'dist_info')
    document = doc_ref.get().to_dict()
    return document["dist_info_list"]


@lru_cache(maxsize=100)
def get_dist_id_from_name_db(dist_name):
    dist_codes = get_all_dist_codes_db()
    name_code_dict = dict((d["dist_name"], d["dist_id"]) for d in dist_codes)
    return name_code_dict.get(dist_name)


@lru_cache(maxsize=100)
def get_dist_name_from_id_db(dist_id):
    dist_codes = get_all_dist_codes_db()
    name_code_dict = dict((d["dist_id"], d["dist_name"]) for d in dist_codes)
    return name_code_dict.get(dist_id)


@cachetools.func.ttl_cache(maxsize=300, ttl=10 * 60)
def get_slots_by_dist_id_db(dist_id):
    key = _get_slot_document_key(dist_id)
    slots_doc = db.collection(u'slots').document(key).get()

    if slots_doc.exists:
        db_slots = slots_doc.to_dict()["vaccine_slots"]

        datetime_format = "%d-%m-%Y %H:%M:%S"
        update_ts = slots_doc.to_dict()["update_ts"]
        update_ts = update_ts.astimezone(timezone('Asia/Kolkata'))
        update_ts = update_ts.strftime(datetime_format)

        res_slots = []

        for slot in db_slots:
            slot["update_ts"] = update_ts
            res_slots.append(slot)

        return res_slots

    return []


def add_subscriber_to_topic(token, dist_id):
    registration_tokens = [token]
    topic = _get_topic_from_dist_id(dist_id)
    response = messaging.subscribe_to_topic(registration_tokens, topic)

    if dist_id not in _get_all_subscribed_dists_from_db():
        doc_ref = db.collection(u'static').document(u'topics_subscribed')
        dist_name = get_dist_name_from_id_db(dist_id)
        doc = {str(dist_id): {"name": dist_name, "count": 0}}
        doc_ref.set(doc, merge=True)

    return response.success_count


def delete_subscriber_from_topic(token, dist_id):
    registration_tokens = [token]
    topic = _get_topic_from_dist_id(dist_id)

    response = messaging.unsubscribe_from_topic(registration_tokens, topic)
    return str(response.success_count)


def send_test_notification(token, dist_name):
    time.sleep(6)
    title = "Test Notification"
    body = "We will notify you when slots would be available in {}".format(dist_name)

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token
    )

    response = messaging.send(message)
    return response


def notify_all_subscribers(dist_id, dist_name, date, num_slots):
    title = "Vaccine Slots Available"
    body = "{} has {} slots on {}".format(dist_name, num_slots, date)

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic=_get_topic_from_dist_id(dist_id)
    )

    response = messaging.send(message)
    print("Notifying : {} ... Response : {}".format(dist_name, str(response)))
    return response


@cachetools.func.ttl_cache(maxsize=200, ttl=1 * 60 * 60)
def get_trend_for_dist_id(dist_id):
    key = _get_slot_document_key(dist_id)
    doc_ref = db.collection(u'trend').document(key).get()

    past_data = doc_ref.to_dict().get("past", []) if doc_ref.exists else []
    datetime_format = "%d-%m-%Y %H:%M:%S"

    response = []
    for data in past_data:
        time_str = data["ts"]
        num_slots = data["num_slots"]
        datetime_obj = datetime.datetime.strptime(time_str, datetime_format)
        time_hour = datetime_obj.hour + datetime_obj.minute / 60
        response.append({"ts": time_str,
                         "ts_hour": time_hour,
                         "num_slots": num_slots})

    return response


def get_all_subscribed_dist_ids(token):
    with open("fcm_auth_key.txt") as f:
        auth_token = f.read()
    auth_key = "key={}".format(auth_token)
    url = "https://iid.googleapis.com/iid/info/{}".format(token)
    response = requests.get(url, params={"details": True}, headers={"Authorization": auth_key})
    print(response.json())
    return list(response.json()["rel"]["topics"].keys())


@cachetools.func.ttl_cache(maxsize=2, ttl=10 * 60)
def _get_all_subscribed_dists_from_db():
    doc = db.collection(u'static').document(u'topics_subscribed').get()
    if doc.exists:
        return list(map(lambda x: int(x), doc.to_dict().keys()))
