import datetime
import time


def get_filtered_dists(search_query, dist_codes):
    search_query = search_query.lower()

    if search_query:
        filtered_dists = list(filter(lambda x: search_query in x['dist_name'].lower()
                                               or search_query in x['state_name'].lower()
                                     , dist_codes))
    else:
        filtered_dists = dist_codes
    return filtered_dists


def sleep_with_activity(message, duration_seconds):
    next_refresh_time = datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds)
    datetime_format = "%d-%m-%Y %H:%M:%S"
    next_refresh_time_str = next_refresh_time.strftime(datetime_format)
    while datetime.datetime.now() < next_refresh_time:
        curr_time_str = datetime.datetime.now().strftime(datetime_format)
        print("\r{} | {}: {}".format(curr_time_str,next_refresh_time_str, message), end="")
        time.sleep(1)
