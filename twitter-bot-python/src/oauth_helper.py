import sys
import requests
import os
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
TOKEN_SECRET = os.environ['TOKEN_SECRET']


def __request_token():
    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri='oob')

    url = "https://api.twitter.com/oauth/request_token"

    try:
        response = oauth.fetch_request_token(url)
        resource_owner_oauth_token = response.get('oauth_token')
        resource_owner_oauth_token_secret = response.get('oauth_token_secret')
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(120)

    return resource_owner_oauth_token, resource_owner_oauth_token_secret


def __get_user_authorization(resource_owner_oauth_token):
    authorization_url = f"https://api.twitter.com/oauth/authorize?oauth_token={resource_owner_oauth_token}"
    authorization_pin = input(
        f" \n Send the following URL to the user you want to generate access tokens for. \n → {authorization_url} \n This URL will allow the user to authorize your application and generate a PIN. \n Paste PIN here: ")

    return (authorization_pin)


def __get_user_access_tokens(resource_owner_oauth_token, resource_owner_oauth_token_secret, authorization_pin):
    oauth = OAuth1Session(CONSUMER_KEY,
                          client_secret=CONSUMER_SECRET,
                          resource_owner_key=resource_owner_oauth_token,
                          resource_owner_secret=resource_owner_oauth_token_secret,
                          verifier=authorization_pin)

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
    return oauth


def connect_to_oauth():
    resource_owner_oauth_token, resource_owner_oauth_token_secret = __request_token()
    authorization_pin = __get_user_authorization(resource_owner_oauth_token)
    return __get_user_access_tokens(resource_owner_oauth_token, resource_owner_oauth_token_secret, authorization_pin)
