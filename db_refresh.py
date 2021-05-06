import time
import random

import requests
from firebase_admin import firestore
from tqdm import tqdm

from api_service import get_all_dist_codes_api, get_dist_vaccination_calendar
from db_service import _get_slot_document_key, notify_all_subscribers, db, get_all_subscribed_dist_ids

# on every 3rd refresh cycle db would be updated, but notification is sent all the time
NUM_DATA_REFRESHED = 1
WAIT_TIME_HRS = 1
NUM_ATTEMPTS_TO_DB_UPDATE = 15
EXP_DELAY_FACTOR = 2
BASE_DELAY = 30


def _should_write_to_db():
    return NUM_DATA_REFRESHED % NUM_ATTEMPTS_TO_DB_UPDATE == 0


def _clear_db(dist_id_to_refresh):
    if _should_write_to_db():
        docs = db.collection(u'slots').where(u'dist_id', u'==', dist_id_to_refresh).stream()
        for doc in docs:
            db.collection(u'slots').document(doc.id).delete()
        return


def _add_slots(dist_id_to_refresh, dist_info_dict):
    slots = get_dist_vaccination_calendar(dist_id_to_refresh)
    slots = slots[0:5]

    info = "{} | {} | {} ".format(dist_info_dict["state_name"], dist_info_dict["dist_name"], len(slots))
    print(info)

    if _should_write_to_db():
        for slot in slots:
            slot["update_ts"] = firestore.SERVER_TIMESTAMP
            key = _get_slot_document_key(slot)
            doc_ref = db.collection(u'slots').document(key)
            doc_ref.set(slot, merge=True)

    # send notification
    if len(slots) >= 1:
        dist_name = dist_info_dict["dist_name"]
        date = slots[0]["date"]
        num_slots = slots[0]["capacity_18_above"]
        notify_all_subscribers(dist_id_to_refresh, dist_name, date, num_slots)


def _refresh_slots(dist_id_to_refresh, dist_info_dict):
    _clear_db(dist_id_to_refresh)
    _add_slots(dist_id_to_refresh, dist_info_dict)


def _refresh_and_get_dist_info_list():
    api_dist_info_list = get_all_dist_codes_api()
    api_dist_info_list = sorted(api_dist_info_list, key=lambda x: x["state_name"])

    # update in firebase
    if _should_write_to_db():
        for dist_info_itr in api_dist_info_list:
            key = str(dist_info_itr["dist_id"])
            doc_ref = db.collection(u'static').document(key)
            print(doc_ref.set(dist_info_itr, merge=True))

    return api_dist_info_list


dist_info_list = _refresh_and_get_dist_info_list()
delay = BASE_DELAY
refreshed_districts = dict()
while True:

    # # Find out the districts that need to be refreshed, instead of refreshing everything
    # try:
    #     subscribed_dist_ids = get_all_subscribed_dist_ids()
    #     subscribed_dist_ids = list(map(lambda x: int(x), subscribed_dist_ids))
    # except Exception as e:
    #     print(e)
    #     print("Could not fetch subscribed dist ids, assuming all ids are needed")
    #     subscribed_dist_ids = list(map(lambda x: x["dist_id"], dist_info_list))

    try:
        for dist_info in tqdm(dist_info_list):
            dist_id = dist_info["dist_id"]

            if dist_id in refreshed_districts:
                continue

            # if dist_id not in subscribed_dist_ids:
            #     continue

            _refresh_slots(dist_id, dist_info)
            refreshed_districts[dist_id] = True
            delay = BASE_DELAY
            # print(refreshed_dicts)

            time.sleep(10 + random.random() * 5)
        print("Done with one refresh, will sleep for {} hours".format(WAIT_TIME_HRS))
        refreshed_districts = dict()
        time.sleep(WAIT_TIME_HRS * 60 * 60)
        NUM_DATA_REFRESHED = NUM_DATA_REFRESHED + 1
    except Exception as e:
        print(e)
        print("something failed, waiting for {} s".format(delay))
        time.sleep(delay)
        delay = delay * EXP_DELAY_FACTOR
