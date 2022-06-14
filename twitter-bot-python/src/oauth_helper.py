import sys
import requests
from requests.auth import HTTPBasicAuth
import os
import logging
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
TOKEN_SECRET = os.environ['TOKEN_SECRET']
TWEETER_USER_NAME = str(os.environ['TWEETER_USER_NAME'])


class OauthHelper:
    def __init__(self):
        self.user_id = None
        self.auth1_session = None
        self.auth1 = None
        self.resource_owner_oauth_token = None
        self.resource_owner_oauth_token_secret = None
        self.authorization_url = None
        self.auth2_token = None

    def start_authorization(self):
        self.auth2_token = self.__get_oauth2_token()
        self.resource_owner_oauth_token, self.resource_owner_oauth_token_secret = self.__request_token()
        self.authorization_url = \
            f"https://api.twitter.com/oauth/authorize?oauth_token={self.resource_owner_oauth_token}"
        return self.authorization_url

    def end_authorization(self, verifier):
        self.auth1_session, self.user_id = self.__get_user_access_tokens(
            self.resource_owner_oauth_token,
            self.resource_owner_oauth_token_secret,
            verifier)
        self.auth1 = self.auth1_session.auth

    @staticmethod
    def __request_token():
        oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri='oob')

        url = "https://api.twitter.com/oauth/request_token"

        response = oauth.fetch_request_token(url)
        resource_owner_oauth_token = response.get('oauth_token')
        resource_owner_oauth_token_secret = response.get('oauth_token_secret')
        return resource_owner_oauth_token, resource_owner_oauth_token_secret

    @staticmethod
    def __get_user_access_tokens(resource_owner_oauth_token, resource_owner_oauth_token_secret, verifier):
        oauth = OAuth1Session(CONSUMER_KEY,
                              client_secret=CONSUMER_SECRET,
                              resource_owner_key=resource_owner_oauth_token,
                              resource_owner_secret=resource_owner_oauth_token_secret,
                              verifier=verifier)

        url = "https://api.twitter.com/oauth/access_token"

        try:
            response = oauth.fetch_access_token(url)
            access_token = response['oauth_token']
            access_token_secret = response['oauth_token_secret']
            user_id = response['user_id']
            screen_name = response['screen_name']
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(120)

        print(f"\n User @handle: {screen_name}", f"\n User ID: {user_id}", f"\n User access token: {access_token}",
              f" \n User access token secret: {access_token_secret} \n")
        return oauth, user_id

    @staticmethod
    def __get_oauth2_token():
        response = requests.post(
            auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET),
            url="https://api.twitter.com/oauth2/token?grant_type=client_credentials",
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }
        )
        assert response.status_code == 200
        return response.json()["access_token"]

    # @staticmethod
    # def __get_user_id(auth2_token):
    #     response = requests.get(
    #         url=f"https://api.twitter.com/2/users/by/username/{TWEETER_USER_NAME}",
    #         headers={
    #             "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    #             "Authorization": f'Bearer {auth2_token}'
    #         }
    #     )
    #     logging.debug(f'get_user_id: TWEETER_USER_NAME = {TWEETER_USER_NAME}, '
    #                   f'response = {response}')
    #     if response.status_code != 200:
    #         raise Exception(f"Cannot find a user {TWEETER_USER_NAME}. "
    #                         f"Response code: {response.status_code}, "
    #                         f"response content: {response.content}")
    #     return response.json()["data"]["id"]
