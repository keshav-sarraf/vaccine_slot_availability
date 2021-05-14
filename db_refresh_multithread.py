import logging
import os
import random
import traceback
from queue import Queue
from threading import Thread
import time

from tqdm import tqdm

from db_refresh import _refresh_and_get_dist_info_list, BASE_DELAY, push_trends_to_db, WAIT_TIME_HRS, EXP_DELAY_FACTOR, \
    NUM_DATA_REFRESHED, _refresh_slots
from db_service import _get_all_subscribed_dists_from_db
from utils import sleep_with_activity

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

os.environ['TZ'] = 'Asia/Kolkata'
time.tzset()


class SlotRefreshWorker(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:

            time.sleep(random.random() * 60)

            # Get the work from the queue and expand the tuple
            dist_info = self.queue.get()
            dist_id = dist_info["dist_id"]

            logger.info("refreshing {}".format(dist_info))

            retry_count_remaining = 10
            while retry_count_remaining:
                try:
                    _refresh_slots(dist_id, dist_info)
                    break
                except Exception as e:
                    logger.error("unable to refresh {}, waiting for a minute".format(dist_info))
                    time.sleep(60)

            self.queue.task_done()


def main():
    ts = time.time()
    subscribed_dists_list = _get_all_subscribed_dists_from_db()
    queue = Queue()
    # Create 8 worker threads
    for x in range(8):
        worker = SlotRefreshWorker(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    # Put the tasks into the queue as a tuple
    pbar = tqdm(_refresh_and_get_dist_info_list())

    for dist_info in pbar:
        dist_id = dist_info["dist_id"]

        if dist_id in subscribed_dists_list:
            logger.info('Queueing {}'.format(dist_id))
            queue.put(dist_info)

    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    logging.info('Took %s', time.time() - ts)


if __name__ == '__main__':
    delay = BASE_DELAY
    refreshed_districts = dict()
    while True:
        try:
            main()
            time.sleep(10 + random.random() * 5)

            NUM_DATA_REFRESHED = NUM_DATA_REFRESHED + 1

            # if NUM_DATA_REFRESHED % 2 == 0:
            #     push_trends_to_db()

            print("num data refreshed : {}".format(NUM_DATA_REFRESHED))
            sleep_with_activity("done for now, will refresh in a bit", WAIT_TIME_HRS * 60 * 60)
        except Exception as e:
            print(traceback.format_exc())
            print("something failed, waiting for {} s".format(delay))
            time.sleep(delay)
            delay = delay * EXP_DELAY_FACTOR
