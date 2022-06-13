import requests
import schedule
import time
import logging
import os
from dotenv import load_dotenv
import threading
from src.oauth_helper import create_oauth1_session, get_oauth2_token, get_user_id

load_dotenv()

UPDATE_WATCHER_TIMEOUT_IN_SECONDS = int(os.environ['UPDATE_WATCHER_TIMEOUT_IN_SECONDS'])
TWEETS_SEARCH_QUERY = str(os.environ['TWEETS_SEARCH_QUERY'])


class TwitterBot:
    def __init__(self):
        self.user_id = None
        self.auth1 = None
        self.auth2_token = None
        self.job = None
        self.thread = None

    def run(self):
        self.thread = threading.Thread(target=self.__run_loop)
        self.thread.start()

    @staticmethod
    def __run_loop():
        while True:
            schedule.run_pending()
            time.sleep(1)

    def is_started(self):
        return self.job is not None

    def start(self):
        if not self.is_started():
            self.__start()
            print("Twitter bot started")
        else:
            print("Twitter bot is already started")

    def __start(self):
        self.__authorize()
        self.job = schedule.every(UPDATE_WATCHER_TIMEOUT_IN_SECONDS) \
            .seconds.do(self.update_watcher)

    def __authorize(self):
        self.auth2_token = get_oauth2_token()
        self.user_id = get_user_id(self.auth2_token)
        self.auth1 = create_oauth1_session().auth

    def stop(self):
        if self.is_started():
            self.__stop()
            print("Twitter bot stopped")
            return 0
        else:
            print("Twitter bot is already stopped")
            return -1

    def __stop(self):
        schedule.cancel_job(self.job)
        self.job = None

    def update_watcher(self):
        print("Update watcher")
        twits = self.fetch_twits()
        self.retweet_twits(twits)

    def fetch_twits(self):
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
                "Authorization": f'Bearer {self.auth2_token}'
            }
        )
        logging.debug(f'fetch_twits: response = {response}')
        if response.status_code != 200:
            logging.error(f'Cannot fetch twits. Response code: {response.status_code}, response content: {response.content}')
        return response.json()

    def create_twit(self, text):
        response = requests.post(
            auth=self.auth1,
            url="https://api.twitter.com/2/tweets",
            json={"text": text},
            headers={
                "Content-Type": "application/json"
            }
        )
        logging.debug(f'create_twit: response = {response}')
        if response.status_code != 201:
            logging.error(f'Twit {text} was not created. Response code: {response.status_code}, response content: {response.content}')

    def retweet_twit(self, twit):
        twit_id = twit['id']
        response = requests.post(
            auth=self.auth1,
            json={
                "tweet_id": f"{twit_id}"
            },
            url=f"https://api.twitter.com/2/users/{self.user_id}/retweets",
            headers={
                "Content-Type": "application/json",
                "Authorization": f'Bearer {self.auth2_token}'
            }
        )
        logging.debug(f'retweet_twit: id = {twit_id}, response = {response}')
        if response.status_code != 200:
            logging.error(f'Twit {twit} was not retweeted. Response code: {response.status_code}, response content: {response.content}')

    def retweet_twits(self, twits):
        for twit in twits["data"]:
            # self.create_twit(auth, twit['text'])
            self.retweet_twit(twit)
