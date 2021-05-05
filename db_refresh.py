import time
import random
from tqdm import tqdm

from api_service import get_all_dist_codes_api, get_dist_vaccination_calendar
from db_service import _get_slot_document_key, send_notification, db


def _clear_db(dist_id_to_refresh):
    docs = db.collection(u'slots').where(u'dist_id', u'==', dist_id_to_refresh).stream()
    for doc in docs:
        db.collection(u'slots').document(doc.id).delete()
    return


def _add_slots(dist_id_to_refresh, dist_info_dict):
    slots = get_dist_vaccination_calendar(dist_id_to_refresh)
    slots = slots[0:7]

    info = "{} | {} | {} ".format(dist_info_dict["state_name"], dist_info_dict["dist_name"], len(slots))
    print(info)

    for slot in slots:
        key = _get_slot_document_key(slot)
        doc_ref = db.collection(u'slots').document(key)
        doc_ref.set(slot, merge=True)

    # send notification
    if len(slots) >= 1:
        dist_name = dist_info_dict["dist_name"]
        date = slots[0]["date"]
        num_slots = slots[0]["capacity_18_above"]
        send_notification(dist_id_to_refresh, dist_name, date, num_slots)


def _refresh_slots(dist_id_to_refresh, dist_info_dict):
    _clear_db(dist_id_to_refresh)
    _add_slots(dist_id_to_refresh, dist_info_dict)


def _refresh_and_get_dist_info_list():
    api_dist_info_list = get_all_dist_codes_api()
    api_dist_info_list = sorted(api_dist_info_list, key=lambda x: x["state_name"])

    # update in firebase
    for dist_info_itr in api_dist_info_list:
        key = str(dist_info_itr["dist_id"])
        doc_ref = db.collection(u'static').document(key)
        print(doc_ref.set(dist_info_itr, merge=True))

    return api_dist_info_list


dist_info_list = _refresh_and_get_dist_info_list()

refreshed_districts = dict()
while True:
    try:
        for dist_info in tqdm(dist_info_list):
            dist_id = dist_info["dist_id"]

            if dist_id in refreshed_districts:
                continue

            _refresh_slots(dist_id, dist_info)
            refreshed_districts[dist_id] = True
            # print(refreshed_dicts)

            time.sleep(1 + random.random() * 5)
        print("Done with one refresh, will sleep for 4 hours")
        refreshed_districts = dict()
        time.sleep(4 * 60 * 60)
    except Exception as e:
        time.sleep(120)
