import json
from functools import lru_cache

import requests


@lru_cache()
def get_all_dist_codes():
    dist_codes = list()

    for state_code in range(1, 42):
        print("State code: ", state_code)
        response = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}".format(state_code))
        json_data = json.loads(response.text)
        for dist_info in json_data["districts"]:
            dist_codes.append({"dist_id": dist_info["district_id"],
                               "dist_name": dist_info["district_name"]}
                              )
    return dist_codes


def get_filtered_dists(search_query):
    dist_codes = get_all_dist_codes()

    if search_query:
        filtered_dists = list(filter(lambda x: search_query in x['dist_name'], dist_codes))
    else:
        filtered_dists = dist_codes

    filtered_dists = list(map(lambda x: x["dist_name"], filtered_dists))

    return filtered_dists

#dist_codes = get_all_dist_codes()
#print(dist_codes)
