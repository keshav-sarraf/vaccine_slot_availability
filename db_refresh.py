import datetime
import time
import random

from firebase_admin import firestore
from tqdm import tqdm

from api_service import get_all_dist_codes_api, get_dist_vaccination_calendar
from db_service import _get_slot_document_key, notify_all_subscribers, db, _get_all_subscribed_dists_from_db, \
    get_all_dist_codes_db

# on every 3rd refresh cycle db would be updated, but notification is sent all the time
from utils import sleep_with_activity

NUM_DATA_REFRESHED = 1
WAIT_TIME_HRS = 0.5
NUM_ATTEMPTS_TO_DB_UPDATE = 5
EXP_DELAY_FACTOR = 2
BASE_DELAY = 30


def _should_write_to_db():
    # need this to keep the db reads and writes to a minimum owing to free tier limitations in firebase
    return NUM_DATA_REFRESHED % NUM_ATTEMPTS_TO_DB_UPDATE == 0


def _clear_db(dist_id_to_refresh):
    if _should_write_to_db():
        key = _get_slot_document_key(dist_id_to_refresh)
        res = db.collection(u'slots').document(key).delete()
        print(res)
    return


def _add_slots(dist_id_to_refresh, dist_info_dict):
    slots = get_dist_vaccination_calendar(dist_id_to_refresh)
    slots = sorted(slots, key=lambda x: x["capacity_18_above"], reverse=True)
    slots = slots[0:5]

    if _should_write_to_db() and len(slots) > 0:
        document = {"vaccine_slots": slots,
                    "update_ts": firestore.SERVER_TIMESTAMP}
        key = _get_slot_document_key(dist_id_to_refresh)
        doc_ref = db.collection(u'slots').document(key)
        doc_ref.set(document)

    # send notification
    if len(slots) >= 1:
        info = "{} | {} | {} ".format(dist_info_dict["state_name"], dist_info_dict["dist_name"], len(slots))
        print(info)

        dist_name = dist_info_dict["dist_name"]
        date = slots[0]["date"]
        num_slots = slots[0]["capacity_18_above"]
        notify_all_subscribers(dist_id_to_refresh, dist_name, date, num_slots)


def _refresh_slots(dist_id_to_refresh, dist_info_dict):
    _clear_db(dist_id_to_refresh)
    _add_slots(dist_id_to_refresh, dist_info_dict)


def _refresh_and_get_dist_info_list():
    api_dist_info_list = get_all_dist_codes_db()

    # update in firebase
    if _should_write_to_db():
        api_dist_info_list = get_all_dist_codes_api()
        api_dist_info_list = sorted(api_dist_info_list, key=lambda x: x["state_name"])
        doc_ref = db.collection(u'static').document(u'dist_info')
        document = {"dist_info_list": api_dist_info_list}
        print(doc_ref.set(document))

    return api_dist_info_list


dist_info_list = _refresh_and_get_dist_info_list()
delay = BASE_DELAY
refreshed_districts = dict()
while True:

    subscribed_dists_list = _get_all_subscribed_dists_from_db()

    try:
        pbar = tqdm(dist_info_list)
        for dist_info in pbar:
            pbar.set_description("Refreshing {} | {} ".format(dist_info["state_name"], dist_info["dist_name"]))
            dist_id = dist_info["dist_id"]

            if dist_id in refreshed_districts:
                continue

            if dist_id not in subscribed_dists_list:
                continue

            _refresh_slots(dist_id, dist_info)
            refreshed_districts[dist_id] = True
            delay = BASE_DELAY
            # print(refreshed_dicts)

            time.sleep(10 + random.random() * 5)

        refreshed_districts = dict()
        NUM_DATA_REFRESHED = NUM_DATA_REFRESHED + 1
        sleep_with_activity("done for now, will refresh in a bit", WAIT_TIME_HRS * 60 * 60)
    except Exception as e:
        print(e)
        print("something failed, waiting for {} s".format(delay))
        time.sleep(delay)
        delay = delay * EXP_DELAY_FACTOR
