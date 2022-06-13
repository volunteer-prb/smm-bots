from src.oauth_helper import create_oauth1_session, get_oauth2_token
from src.twitter_bot import TwitterBot
import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

TWEETER_USER_NAME = str(os.environ['TWEETER_USER_NAME'])


def get_user_id(auth2_token):
    response = requests.get(
        url=f"https://api.twitter.com/2/users/by/username/{TWEETER_USER_NAME}",
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Authorization": f'Bearer {auth2_token}'
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
    auth2_token = get_oauth2_token()
    user_id = get_user_id(auth2_token)
    auth1 = create_oauth1_session().auth

    bot = TwitterBot(user_id=user_id, auth2_token=auth2_token, auth1=auth1)
    bot.start()
    bot.run()

