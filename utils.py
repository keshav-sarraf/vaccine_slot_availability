import datetime
import time
from math import floor


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
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(seconds=duration_seconds)
    datetime_format = "%d-%m-%Y %H:%M:%S"
    end_time_str = end_time.strftime(datetime_format)

    while datetime.datetime.now() < end_time:
        curr_time = datetime.datetime.now()
        curr_time_str = curr_time.strftime(datetime_format)

        progress_sec = (curr_time - start_time).total_seconds() + 2
        progress_percent = min(1.0, progress_sec / duration_seconds)
        num_total_bars = 10
        num_finished_bars = floor(progress_percent * num_total_bars)
        num_remaining_bars = num_total_bars - num_finished_bars
        bars = ["#"] * num_finished_bars + [" "] * num_remaining_bars
        bars_str = "".join(bars)

        print("\r{} | {}: [{}] : {}".format(curr_time_str, end_time_str, bars_str, message), end="")
        time.sleep(1)
