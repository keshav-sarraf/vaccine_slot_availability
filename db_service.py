import datetime
import random
import time
from functools import lru_cache

from firebase_admin import firestore

# Use the application default credentials
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

from api_service import get_all_dist_codes_api, get_dist_vaccination_calendar

cred = credentials.Certificate("vaccineslotavailability-firebase-adminsdk-6jiff-78515b332d.json")
firebase_admin.initialize_app(cred)
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


def get_slots_by_dist_id(dist_id):
    slots_ref = db.collection(u'slots')
    docs = slots_ref.where(u'dist_id', u'==', dist_id).stream()

    slots = []
    for doc in docs:
        slots.append(doc.to_dict())

    return slots


def add_subscriber_to_topic(token, dist_id):
    # TODO: validate

    registration_tokens = [token]
    topic = _get_topic_from_dist_id(dist_id)

    response = messaging.subscribe_to_topic(registration_tokens, topic)
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


def refresh_slots_data_and_notify():
    dist_info_list = get_all_dist_codes_api()
    dist_info_list = sorted(dist_info_list, key=lambda x: x["state_name"])

    for dist_info in dist_info_list:
        dist_id = dist_info["dist_id"]
        slots = get_dist_vaccination_calendar(dist_id)

        info = "{} | {} | {} ".format(dist_info["state_name"], dist_info["dist_name"], len(slots))
        print(info)

        for slot in slots:
            key = _get_slot_document_key(slot)
            doc_ref = db.collection(u'slots').document(key)
            doc_ref.set(slot, merge=True)

        # send notification
        if len(slots) >= 1:
            dist_name = dist_info["dist_name"]
            date = slots[0]["date"]
            num_slots = slots[0]["capacity_18_above"]
            send_notification(dist_id, dist_name, date, num_slots)

        time.sleep(random.random() * 5)
    return


def create_static_data_in_db():
    dist_info_list = get_all_dist_codes_api()
    for dist_info in dist_info_list:
        dist_id = dist_info["dist_id"]

        key = str(dist_id)
        doc_ref = db.collection(u'static').document(key)
        print(doc_ref.set(dist_info, merge=True))
    return


#create_static_data_in_db()
refresh_slots_data_and_notify()
# create_static_data_in_db()
#print(get_all_dist_codes_db())

# TODO: check the slots, if they are full then delete from the db
