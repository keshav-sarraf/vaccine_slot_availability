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


dist_info_list = get_all_dist_codes_api()
dist_info_list = sorted(dist_info_list, key=lambda x: x["state_name"])

# for dist_info in dist_info_list:
#     dist_id = dist_info["dist_id"]
#
#     key = str(dist_id)
#     doc_ref = db.collection(u'static').document(key)
#     print(doc_ref.set(dist_info, merge=True))

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
        refreshed_districts = dict()
    except Exception as e:
        time.sleep(120)
