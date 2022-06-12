from src.oauth_helper import create_oauth1_session, get_oauth2_token
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
TWEETS_SEARCH_QUERY = str(os.environ['TWEETS_SEARCH_QUERY'])

# update_watcher_counter = 0
# update_watcher_counter_string = ''.join(random.choice(string.ascii_letters) for i in range(10))


def update_watcher(auth1, auth2Token):
    print("Update watcher")
    twits = fetch_twits(auth2Token)
    retweet_twits(auth1, twits)
    # global update_watcher_counter
    # update_watcher_counter = update_watcher_counter + 1
    # create_twit(auth1, update_watcher_counter_string + ' ' + str(update_watcher_counter))


def fetch_twits(auth2Token):
    query_params = {
        'query': TWEETS_SEARCH_QUERY,
        # 'start_time': start_date,
        # 'end_time': end_date,
        'max_results': 10,
        'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
        'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
        'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
        'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
        'next_token': {}
    }
    response = requests.get(
        url="https://api.twitter.com/2/tweets/search/recent",
        params=query_params,
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {auth2Token}'
        }
    )
    logging.debug(f'fetch_twits: response = {response}')
    if response.status_code != 200:
        logging.error(f'Cannot fetch twits. Response code: {response.status_code}, response content: {response.content}')
    return response.json()


def create_twit(auth, text):
    response = requests.post(
        auth=auth,
        url="https://api.twitter.com/2/tweets",
        json={"text": text},
        headers={"Content-Type": "application/json"}
    )
    logging.debug(f'create_twit: response = {response}')
    if response.status_code != 201:
        logging.error(f'Twit {text} was not created. Response code: {response.status_code}, response content: {response.content}')


# def retweet_twits(auth, twits):
#     for twit in twits["data"]:
#         twit_id = twit['id']
#         response = requests.post(
#             auth=auth,
#             url=f"https://api.twitter.com/1.1/statuses/retweet/{twit_id}.json",
#             headers={"Content-Type": "application/json"}
#         )
#         logging.debug(f'retweet_twit: id = {twit_id}, response = {response}')
#         if response.status_code != 201:
#             logging.error(f'Twit {twit} was not retweeted. Response code: {response.status_code}, response content: {response.content}')


def retweet_twits(auth, twits):
    for twit in twits["data"]:
        twit_text = twit['text']
        create_twit(auth, twit_text)


if __name__ == '__main__':
    print("Twitter Bot started")
    auth2Token = get_oauth2_token()
    auth1 = create_oauth1_session().auth
    schedule.every(UPDATE_WATCHER_TIMEOUT_IN_SECONDS).seconds.do(update_watcher, auth1, auth2Token)
    while True:
        schedule.run_pending()
        time.sleep(1)
