import base64
import json
import os
import time
from functools import lru_cache

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


@lru_cache()
def get_all_dist_codes_db():
    doc_ref = db.collection(u'static').document(u'dist_info')
    document = doc_ref.get().to_dict()
    return document["dist_info_list"]


@lru_cache(maxsize=100)
def get_dist_id_from_name_db(dist_name):
    dist_codes = get_all_dist_codes_db()
    name_code_dict = dict((d["dist_name"], d["dist_id"]) for d in dist_codes)
    return name_code_dict.get(dist_name)


@lru_cache(maxsize=300)
def get_slots_by_dist_id_db(dist_id):
    key = _get_slot_document_key(dist_id)
    slots_ref = db.collection(u'slots').document(key)
    doc = slots_ref.get()
    db_slots = doc.to_dict()["vaccine_slots"]

    datetime_format = "%d-%m-%Y %H:%M:%S"

    res_slots = []
    for slot in db_slots:
        slot["update_ts"] = slot["update_ts"].astimezone(timezone('Asia/Kolkata'))
        slot["update_ts"] = slot["update_ts"].strftime(datetime_format)
        res_slots.append(slot)

    return res_slots


def add_subscriber_to_topic(token, dist_id):
    registration_tokens = [token]
    topic = _get_topic_from_dist_id(dist_id)
    response = messaging.subscribe_to_topic(registration_tokens, topic)

    doc_ref = db.collection(u'static').document(u'topics_subscribed')
    doc_ref.set({str(dist_id), True}, merge=True)

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
    return response


def get_all_subscribed_dist_ids():
    token = "fBmfeH-v8_WxMZ41tDHDb8:APA91bGKvt9zqIUkwW45gr5-FUZgYGY5ZQzbdiamU02-lZ0RdeiGQxjhj_F5TE7qy3k7Fj7iuoFxD2" \
            "-otc72B5ExLKSv6fWilljvokizTp9kEEk0ufuT9UuqVU-jDflZEvdVDuzjxJIQ"
    with open("fcm_auth_key.txt") as f:
        auth_token = f.read()
    auth_key = "key={}".format(auth_token)
    url = "https://iid.googleapis.com/iid/info/{}".format(token)
    response = requests.get(url, params={"details": True}, headers={"Authorization": auth_key})
    print(response.json())
    return list(response.json()["rel"]["topics"].keys())


def _get_all_subscribed_dists_from_db():
    doc = db.collection(u'static').document(u'topics_subscribed')
    if doc.exists:
        return list(map(lambda x: int(x), doc.get().to_dict().keys()))
