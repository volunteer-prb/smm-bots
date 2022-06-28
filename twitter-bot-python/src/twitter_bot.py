import requests
import schedule
import time
import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import threading
from src.oauth_helper import OauthHelper

load_dotenv()

UPDATE_WATCHER_TIMEOUT_IN_SECONDS = int(os.environ['UPDATE_WATCHER_TIMEOUT_IN_SECONDS'])
TWEETS_SEARCH_QUERY = str(os.environ['TWEETS_SEARCH_QUERY'])


class TwitterBot:
    def __init__(self):
        self.oauth_helper = None
        self.job = None
        self.thread = None
        self.start_time = None
        self.end_time = None

    def run(self):
        # self.start_time = datetime.utcnow() - timedelta(seconds=30)
        self.thread = threading.Thread(target=self.__run_loop)
        self.thread.start()

    @staticmethod
    def __run_loop():
        while True:
            schedule.run_pending()
            time.sleep(1)

    def is_started(self):
        return self.job is not None

    def start_authorization(self):
        if self.is_started():
            raise RuntimeError("Service already started. Stop service and start authorization again")
        self.oauth_helper = OauthHelper()
        authorization_url = self.oauth_helper.start_authorization()
        print(f"Service authorization is started. Authorization link is {authorization_url}")
        return authorization_url

    def start(self, verifier):
        if self.is_started():
            raise RuntimeError("Service already started. Stop service and start authorization again")
        if self.oauth_helper is None:
            raise RuntimeError("Authorization is not started. Start authorization and start service again")
        self.oauth_helper.end_authorization(verifier)
        self.job = schedule.every(UPDATE_WATCHER_TIMEOUT_IN_SECONDS) \
            .seconds.do(self.update_watcher)
        print("Service is started")

    def stop(self):
        if not self.is_started():
            raise RuntimeError("Service is not started. Cannot stopp service")
        schedule.cancel_job(self.job)
        self.oauth_helper = None
        self.job = None
        print("Service stopped")

    def update_watcher(self):
        print("Update watcher")
        twits = self.fetch_twits()
        self.retweet_twits(twits)

    def fetch_twits(self):
        self.end_time = datetime.utcnow() - timedelta(seconds=30)
        query_params = {
            'query': TWEETS_SEARCH_QUERY,
            # 'start_time': self.__get_formatted_time(self.start_time),
            # 'end_time': self.__get_formatted_time(self.end_time),
            # 'max_results': 10,
            'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
            'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
            'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
            'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
            'next_token': {}
        }
        if self.start_time is not None:
            query_params['start_time'] = self.__get_formatted_time(self.start_time)
        if self.end_time is not None:
            query_params['end_time'] = self.__get_formatted_time(self.end_time)
        response = requests.get(
            url="https://api.twitter.com/2/tweets/search/recent",
            params=query_params,
            headers={
                "Content-Type": "application/json",
                "Authorization": f'Bearer {self.oauth_helper.auth2_token}'
            }
        )
        logging.debug(f'fetch_twits: response = {response}')
        self.start_time = self.end_time
        if response.status_code != 200:
            logging.error(f'Cannot fetch twits. Response code: {response.status_code}, response content: {response.content}')
        return response.json()

    @staticmethod
    def __get_formatted_time(the_time: datetime):
        if datetime is None:
            return "null"
        return the_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    def create_twit(self, text):
        response = requests.post(
            auth=self.oauth_helper.auth1,
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
            auth=self.oauth_helper.auth1,
            json={
                "tweet_id": f"{twit_id}"
            },
            url=f"https://api.twitter.com/2/users/{self.oauth_helper.user_id}/retweets",
            headers={
                "Content-Type": "application/json",
                "Authorization": f'Bearer {self.oauth_helper.auth2_token}'
            }
        )
        logging.debug(f'retweet_twit: id = {twit_id}, response = {response}')
        if response.status_code != 200:
            logging.error(f'Twit {twit} was not retweeted. Response code: {response.status_code}, response content: {response.content}')

    def retweet_twits(self, twits):
        if twits['meta']['result_count'] > 0:
            for twit in reversed(twits["data"]):
                # self.create_twit(auth, twit['text'])
                self.retweet_twit(twit)
