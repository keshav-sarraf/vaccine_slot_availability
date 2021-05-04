import time
import random

from api_service import get_all_dist_codes_api, get_dist_vaccination_calendar
from db_service import _get_slot_document_key, send_notification, db


def _refresh_dist(dist_id_to_refresh):
    slots = get_dist_vaccination_calendar(dist_id_to_refresh)

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
        send_notification(dist_id_to_refresh, dist_name, date, num_slots)


dist_info_list = get_all_dist_codes_api()
dist_info_list = sorted(dist_info_list, key=lambda x: x["state_name"])

refreshed_dicts = dict()
while True:
    try:
        for dist_info in dist_info_list:
            dist_id = dist_info["dist_id"]

            if dist_id in refreshed_dicts:
                continue

            _refresh_dist(dist_id)
            refreshed_dicts[dist_id] = True

            time.sleep(5 + random.random() * 5)
    except Exception as e:
        time.sleep(300)

    refreshed_dicts = dict()
