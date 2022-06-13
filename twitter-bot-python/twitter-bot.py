from src.oauth_helper import create_oauth1_session, get_oauth2_token
import requests
import schedule
import time
import logging
import os
from dotenv import load_dotenv

load_dotenv()

TWEETER_USER_NAME = str(os.environ['TWEETER_USER_NAME'])
UPDATE_WATCHER_TIMEOUT_IN_SECONDS = int(os.environ['UPDATE_WATCHER_TIMEOUT_IN_SECONDS'])
TWEETS_SEARCH_QUERY = str(os.environ['TWEETS_SEARCH_QUERY'])


def update_watcher(auth1, user_id, auth2Token):
    print("Update watcher")
    twits = fetch_twits(auth2Token)
    retweet_twits(auth1, user_id, twits)


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
        headers={
            "Content-Type": "application/json"
        }
    )
    logging.debug(f'create_twit: response = {response}')
    if response.status_code != 201:
        logging.error(f'Twit {text} was not created. Response code: {response.status_code}, response content: {response.content}')


def retweet_twit(auth, user_id, twit):
    twit_id = twit['id']
    response = requests.post(
        auth=auth,
        json={
            "tweet_id": f"{twit_id}"
        },
        url=f"https://api.twitter.com/2/users/{user_id}/retweets",
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {auth2Token}'
        }
    )
    logging.debug(f'retweet_twit: id = {twit_id}, response = {response}')
    if response.status_code != 200:
        logging.error(f'Twit {twit} was not retweeted. Response code: {response.status_code}, response content: {response.content}')


def retweet_twits(auth, user_id, twits):
    for twit in twits["data"]:
        # create_twit(auth, twit['text'])
        retweet_twit(auth, user_id, twit)


def get_user_id(auth2Token):
    response = requests.get(
        url=f"https://api.twitter.com/2/users/by/username/{TWEETER_USER_NAME}",
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Authorization": f'Bearer {auth2Token}'
        }
    )
    logging.debug(f'get_user_id: TWEETER_USER_NAME = {TWEETER_USER_NAME}, '
                  f'response = {response}')
    if response.status_code != 200:
        raise Exception(f"Cannot find a user {TWEETER_USER_NAME}. "
                        f"Response code: {response.status_code}, "
                        f"response content: {response.content}")
    return response.json()["data"]["id"]


if __name__ == '__main__':
    print("Twitter Bot started")
    auth2Token = get_oauth2_token()
    auth1 = create_oauth1_session().auth
    user_id = get_user_id(auth2Token)
    schedule.every(UPDATE_WATCHER_TIMEOUT_IN_SECONDS)\
        .seconds.do(update_watcher, auth1,user_id, auth2Token)
    while True:
        schedule.run_pending()
        time.sleep(1)
