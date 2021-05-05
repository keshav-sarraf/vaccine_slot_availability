import base64
import json
import os
from functools import lru_cache

from firebase_admin import firestore

# Use the application default credentials
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

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


def _get_slot_document_key(slot):
    return "date_{}_center_{}".format(slot["date"], slot["center_id"])


@lru_cache()
def get_all_dist_codes_db():
    dist_info_db = db.collection(u'static').get()

    dist_info_list = list()
    for dist_info in dist_info_db:
        dist_info_list.append(dist_info.to_dict())

    return dist_info_list


@lru_cache()
def get_dist_id_from_name_db(dist_name):
    dist_codes = get_all_dist_codes_db()
    name_code_dict = dict((d["dist_name"], d["dist_id"]) for d in dist_codes)
    return name_code_dict.get(dist_name)


def get_slots_by_dist_id_db(dist_id):
    slots_ref = db.collection(u'slots')
    docs = slots_ref.where(u'dist_id', u'==', dist_id).stream()

    slots = []
    for doc in docs:
        slots.append(doc.to_dict())

    return slots


def add_subscriber_to_topic(token, dist_id):
    registration_tokens = [token]
    topic = _get_topic_from_dist_id(dist_id)

    response = messaging.subscribe_to_topic(registration_tokens, topic)
    return response.success_count


def delete_subscriber_from_topic(token, dist_id):
    registration_tokens = [token]
    topic = _get_topic_from_dist_id(dist_id)

    response = messaging.unsubscribe_from_topic(registration_tokens, topic)
    return str(response.success_count)


def send_notification(dist_id, dist_name, date, num_slots):
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


def create_static_data_in_db():
    dist_info_list = get_all_dist_codes_api()
    for dist_info in dist_info_list:
        dist_id = dist_info["dist_id"]

        key = str(dist_id)
        doc_ref = db.collection(u'static').document(key)
        print(doc_ref.set(dist_info, merge=True))
    return
