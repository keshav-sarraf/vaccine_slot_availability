import json
import os
from datetime import datetime
from functools import lru_cache
from urllib.parse import urljoin

import requests


# TODO: fix this
# ROOT_URL = r"https://cdn-api.co-vin.in/api"

def get_all_state_codes():
    headers = {'Content-type': 'application/json', 'accept': 'application/json', 'Accept-Language': 'hi_IN'}
    response = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/states", headers=headers)
    json_data = response.json()["states"]
    return json_data


@lru_cache()
def get_all_dist_codes():
    dist_codes = list()

    states = get_all_state_codes()

    for state in states:
        print("State: ", state)
        response = requests.get(
            "https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}".format(state["state_id"]))
        json_data = json.loads(response.text)
        for dist_info in json_data["districts"]:
            dist_codes.append({"dist_id": dist_info["district_id"],
                               "dist_name": dist_info["district_name"],
                               "state_id": state["state_id"],
                               "state_name": state["state_name"]}
                              )
    return dist_codes


def get_filtered_dists(search_query):
    dist_codes = get_all_dist_codes()

    if search_query:
        filtered_dists = list(filter(lambda x: search_query in x['dist_name'].lower()
                                               or search_query in x['state_name'].lower()
                                     , dist_codes))
    else:
        filtered_dists = dist_codes
    return filtered_dists


def get_dist_vaccination_calendar(dist_id):
    url = r"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
    params = {"district_id": dist_id,
              "date": "15-05-2021"}

    response = requests.get(url, params=params)
    data = response.json()

    slots = []

    print(data)

    for center_info in data["centers"]:
        slot_info = {
            "center_name": center_info["name"],
            "state_name": center_info["state_name"],
            "dist_name": center_info["district_name"],
            "block_name": center_info["block_name"],
            "pincode": center_info["pincode"],
        }

        for session in center_info["sessions"]:
            datetimeobject = datetime.strptime(session["date"], '%d-%m-%Y')
            new_format = datetimeobject.strftime('%d%b')

            session_info = {
                "date": new_format,
                "available_capacity": session["available_capacity"],
                "min_age_limit": session["min_age_limit"]
            }

            combined_info = {**slot_info, **session_info}
            slots.append(combined_info)

    return slots



# print(get_dist_vaccination_calendar("512")[0])
