from src.oauth_helper import connect_to_oauth
import requests
import string
import random
import schedule
import time
import logging
import os
from dotenv import load_dotenv

load_dotenv()

UPDATE_WATCHER_TIMEOUT_IN_SECONDS = int(os.environ['UPDATE_WATCHER_TIMEOUT_IN_SECONDS'])

update_watcher_counter = 0
update_watcher_counter_string = ''.join(random.choice(string.ascii_letters) for i in range(10))


def update_watcher(auth):
    print("Update watcher")
    global update_watcher_counter
    update_watcher_counter = update_watcher_counter + 1
    response = requests.post(
        auth=auth,
        url="https://api.twitter.com/2/tweets",
        json={"text": update_watcher_counter_string + ' ' + str(update_watcher_counter)},
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 201


if __name__ == '__main__':
    print("Twitter Bot started")
    auth = connect_to_oauth().auth
    schedule.every(UPDATE_WATCHER_TIMEOUT_IN_SECONDS).seconds.do(update_watcher, auth)
    while True:
        schedule.run_pending()
        time.sleep(1)
