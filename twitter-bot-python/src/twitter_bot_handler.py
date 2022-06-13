from http.server import BaseHTTPRequestHandler
from src.twitter_bot import TwitterBot
import logging
import json


class TwitterBotHandler(BaseHTTPRequestHandler):
    def __init__(self, twitter_bot: TwitterBot, *args, **kwargs):
        self.twitter_bot = twitter_bot
        super().__init__(*args, **kwargs)

    def do_GET(self):
        logging.debug(f"do_GET: self.path={self.path}")
        if self.path == '/' or self.path == '/status':
            self.__send_ok_response(self.__get_status_response())
        elif self.path == '/start':
            self.twitter_bot.start()
            self.__send_ok_response(self.__get_status_response())
        elif self.path == '/stop':
            self.twitter_bot.stop()
            self.__send_ok_response(self.__get_status_response())
        else:
            self.__send_invalid_request_response(f"The endpoint {self.path} is not supported")

    def __get_status_response(self):
        return {"status": f"{self.__get_bot_status()}"}

    def __get_bot_status(self):
        if self.twitter_bot.is_started():
            return "started"
        else:
            return "stopped"

    def __send_ok_response(self, obj):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("utf-8"))

    def __send_invalid_request_response(self, error_message):
        self.send_response(400)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {
                    "error_message": error_message
                 }
            ).encode("utf-8")
        )
