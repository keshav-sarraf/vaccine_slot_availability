import json
from datetime import datetime, timedelta
from functools import lru_cache
import logging
import requests

# logging.basicConfig(level=logging.DEBUG)

resp = requests.get("http://ip-api.com/json")
print(resp.json())


# TODO: fix this
# ROOT_URL = r"https://cdn-api.co-vin.in/api"

def get_all_state_codes():
    headers = {'Content-type': 'application/json', 'accept': 'application/json', 'Accept-Language': 'hi_IN'}
    response = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/states", headers=headers)

    if response.status_code != 200:
        print(response.text)

    json_data = response.json()["states"]
    return json_data


@lru_cache()
def get_all_dist_codes_api():
    dist_codes = list()

    states = get_all_state_codes()

    for state in states:
        # print("State: ", state)
        response = requests.get(
            "https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}".format(state["state_id"]))
        print(response.json())
        json_data = json.loads(response.text)
        for dist_info in json_data["districts"]:
            dist_codes.append({"dist_id": dist_info["district_id"],
                               "dist_name": dist_info["district_name"],
                               "state_id": state["state_id"],
                               "state_name": state["state_name"]}
                              )
    return dist_codes


@lru_cache()
def get_dist_id_from_name_api(dist_name):
    dist_codes = get_all_dist_codes_api()
    name_code_dict = dict((d["dist_name"], d["dist_id"]) for d in dist_codes)
    return name_code_dict.get(dist_name)


def get_dist_vaccination_calendar_by_date(dist_id, date):
    url = r"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
    params = {"district_id": str(dist_id),
              "date": date}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(response.text)

    data = response.json()

    slots = []

    # print(data)

    for center_info in data["centers"]:
        slot_info = {
            "center_id": center_info["center_id"],
            "center_name": center_info["name"],
            "state_name": center_info["state_name"],
            "dist_name": center_info["district_name"],
            "block_name": center_info["block_name"],
            "pincode": center_info["pincode"],
            "dist_id": dist_id,
        }

        for session in center_info["sessions"]:
            datetimeobject = datetime.strptime(session["date"], '%d-%m-%Y')
            new_format = datetimeobject.strftime('%d%b')
            min_age_limit = session["min_age_limit"]

            session_info = {
                "date": new_format,
                "capacity_18_above": session["available_capacity"] if min_age_limit == 18 else 0,
                "capacity_45_above": session["available_capacity"] if min_age_limit == 45 else 0,
                "vaccine": session["vaccine"]
            }

            combined_info = {**slot_info, **session_info}
            slots.append(combined_info)

    slots = list(filter(lambda x: x["capacity_18_above"] > 0, slots))
    return slots


def get_dist_vaccination_calendar(dist_id):
    date_today = datetime.today()
    slots = []

    date = date_today

    for i in range(4):
        date_string = datetime.strftime(date, '%d-%m-%Y')
        # print(date_string, "\n")
        week_slots = get_dist_vaccination_calendar_by_date(dist_id, date_string)
        slots = slots + week_slots
        date = date + timedelta(days=8)

    return slots

# print(get_dist_vaccination_calendar("512")[0])
