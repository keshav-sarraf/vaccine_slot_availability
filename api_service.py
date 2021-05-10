import json
import random
import time
from datetime import datetime, timedelta
from functools import lru_cache
import logging
import requests

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

# logging.basicConfig(level=logging.DEBUG)
# https://stackoverflow.com/questions/27652543/how-to-use-python-requests-to-fake-a-browser-visit-a-k-a-and-generate-user-agent
from tqdm import tqdm

resp = requests.get("http://ip-api.com/json")
print(resp.json())

software_names = [SoftwareName.CHROME.value,
                  SoftwareName.FIREFOX.value,
                  SoftwareName.EDGE.value]
operating_systems = [OperatingSystem.WINDOWS.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)


# TODO: fix this
# ROOT_URL = r"https://cdn-api.co-vin.in/api"

def get_all_state_codes():
    headers = headers = {'Content-type': 'application/json',
                         'accept': 'application/json, text/plain, */*',
                         'sec-ch-ua-mobile': '?0',
                         'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                         'User-Agent': user_agent_rotator.get_random_user_agent(),
                         'referer': r'https://www.cowin.gov.in/',
                         'origin': r'https://www.cowin.gov.in'}

    for i in range(10):
        try:
            response = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/states", headers=headers)

            if response.status_code != 200:
                print(response.text)

            json_data = response.json()["states"]
            return json_data
        except Exception as e:
            print(e)
            print("unable to get states attempt {}".format(i))
            time.sleep(10 + random.random() * 30 + random.random() * 30)

    raise Exception("Unable to get list of states")


@lru_cache()
def get_all_dist_codes_api():
    dist_codes = list()

    states = get_all_state_codes()

    for state in tqdm(states):
        headers = {'Content-type': 'application/json',
                   'accept': 'application/json, text/plain, */*',
                   'sec-ch-ua-mobile': '?0',
                   'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                   'User-Agent': user_agent_rotator.get_random_user_agent(),
                   'referer': r'https://www.cowin.gov.in/',
                   'origin': r'https://www.cowin.gov.in'}

        success = False
        for i in range(10):
            try:
                response = requests.get(
                    "https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}".format(state["state_id"]),
                    headers=headers)
                print(state["state_name"])
                json_data = json.loads(response.text)

                for dist_info in json_data["districts"]:
                    dist_codes.append({"dist_id": dist_info["district_id"],
                                       "dist_name": dist_info["district_name"],
                                       "state_id": state["state_id"],
                                       "state_name": state["state_name"]}
                                      )
                success = True
                break
            except Exception as e:
                print(e)
                print("unable to get dist info attempt {}".format(i))
                time.sleep(3 * 60 + random.random() * 30)

        if not success:
            raise Exception("Unable to get dist info for state {}".format(state["state_name"]))

        time.sleep(10 + random.random() * 10)
    return dist_codes


@lru_cache()
def get_dist_id_from_name_api(dist_name):
    dist_codes = get_all_dist_codes_api()
    name_code_dict = dict((d["dist_name"], d["dist_id"]) for d in dist_codes)
    return name_code_dict.get(dist_name)


def get_dist_vaccination_calendar_by_date(dist_id, date, user_agent=user_agent_rotator.get_random_user_agent()):
    headers = {'Content-type': 'application/json',
               'accept': 'application/json, text/plain, */*',
               'sec-ch-ua-mobile': '?0',
               'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
               'User-Agent': user_agent,
               'referer': r'https://www.cowin.gov.in/',
               'origin': r'https://www.cowin.gov.in'}

    url = r"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
    params = {"district_id": str(dist_id),
              "date": date}

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        print("Non 200 data received for dist_id {} date {}".format(dist_id, date))
        print(response.text)

    data = response.json()

    slots = []

    if "centers" not in data:
        print("Invalid data received for dist_id {} date {}".format(dist_id, date))
        print(data)
    # print(data)

    for center_info in data.get("centers", []):
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
        week_slots = get_dist_vaccination_calendar_by_date(dist_id,
                                                           date_string,
                                                           user_agent=user_agent_rotator.get_random_user_agent())
        slots = slots + week_slots
        date = date + timedelta(days=8)

        if len(slots) >= 5:
            break

        time.sleep(1 + random.random() * 2)

    return slots


# print(get_dist_vaccination_calendar(363))
