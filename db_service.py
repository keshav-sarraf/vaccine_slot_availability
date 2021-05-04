import datetime
import random
import time

from firebase_admin import firestore

# Use the application default credentials
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

from api_service import get_all_dist_codes, get_dist_vaccination_calendar

cred = credentials.Certificate("vaccineslotavailability-firebase-adminsdk-6jiff-78515b332d.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def _get_topic_from_dist_id(dist_id):
    return "/topics/{}".format(dist_id)

def add_subscriber_to_topic(token, dist_id):
    # TODO: validate

    registration_tokens = [token]
    topic = _get_topic_from_dist_id(dist_id)

    response = messaging.subscribe_to_topic(registration_tokens, topic)
    return str(response.success_count)


def refresh_slots_in_db():
    dist_info_list = get_all_dist_codes()
    dist_info_list = sorted(dist_info_list, key=lambda x: x["state_name"])

    for dist_info in dist_info_list:
        dist_id = dist_info["dist_id"]
        slots = get_dist_vaccination_calendar(dist_id)

        info = "{} | {} | {} ".format(dist_info["state_name"], dist_info["dist_name"], len(slots))
        print(info)

        for slot in slots:
            key = "date_{}_center_{}".format(slot["date"], slot["center_id"])
            doc_ref = db.collection(u'slots').document(key)
            doc_ref.set(slot, merge=True)
        time.sleep(random.random() * 5)
    return


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

# refresh_slots_in_db()

# TODO: check the slots, if they are full then delete from the db