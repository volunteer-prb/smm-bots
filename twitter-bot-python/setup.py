from src.twitter_bot import TwitterBot
from src.twitter_bot_handler import TwitterBotHandler
import requests
import logging
import os
from dotenv import load_dotenv
from http.server import HTTPServer
from functools import partial

load_dotenv()

TWEETER_USER_NAME = str(os.environ['TWEETER_USER_NAME'])
SERVER_PORT = int(os.environ['SERVER_PORT'])
HOST_NAME = "localhost"


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
    bot = TwitterBot()
    bot.run()

    handler = partial(TwitterBotHandler, bot)
    server = HTTPServer((HOST_NAME, SERVER_PORT), handler)
    print("Twitter Bot Server started http://%s:%s" % (HOST_NAME, SERVER_PORT))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    print("Twitter Bot Server stopped.")
