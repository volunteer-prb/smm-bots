from http.server import BaseHTTPRequestHandler
from src.twitter_bot import TwitterBot
from src.html_generator import HtmlGenerator
import logging
import json
import sys
if (3, 0) <= sys.version_info:
    from urllib.parse import urlparse
elif (2, 0) <= sys.version_info <= (2, 9):
    from urlparse import urlparse


class TwitterBotHandler(BaseHTTPRequestHandler):
    def __init__(self, twitter_bot: TwitterBot, *args, **kwargs):
        self.twitter_bot = twitter_bot
        super().__init__(*args, **kwargs)

    def do_GET(self):
        logging.debug(f"do_GET: self.path={self.path}")
        if self.path == '/' or self.path == '/status':
            self.__send_ok_response(self.__get_status_response())
        elif self.path == '/authorization-url':
            authorization_url = self.twitter_bot.start_authorization()
            self.__send_ok_response({"url": f"{authorization_url}"})
        elif self.path == '/list':
            twits, end_time = self.twitter_bot.fetch_twits_of_day('')
            self.__send_ok_response(twits)
        elif self.path.startswith('/list?'):
            twits, end_time = self.twitter_bot.fetch_twits_of_day(urlparse(self.path).query)
            self.__send_ok_response(twits)
        elif self.path == '/list/html':
            twits, end_time = self.twitter_bot.fetch_twits_of_day('')
            self.__send_ok_html_response(HtmlGenerator().render(twits, end_time))
        elif self.path.startswith('/list/html?'):
            twits, end_time = self.twitter_bot.fetch_twits_of_day(urlparse(self.path).query)
            self.__send_ok_html_response(HtmlGenerator().render(twits, end_time))
        else:
            self.__send_invalid_request_response(f"The endpoint GET {self.path} is not supported")

    def do_POST(self):
        logging.debug(f"do_POST: self.path={self.path}")
        if self.path == '/start':
            verifier = self.__read_body()['verifier']
            self.twitter_bot.start(verifier)
            self.__send_ok_response(self.__get_status_response())
        elif self.path == '/stop':
            self.twitter_bot.stop()
            self.__send_ok_response(self.__get_status_response())
        else:
            self.__send_invalid_request_response(f"The endpoint POST {self.path} is not supported")

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
        self.wfile.write(json.dumps(obj).encode('utf-8'))

    def __send_ok_html_response(self, text_html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(text_html, 'utf-8'))

    def __send_invalid_request_response(self, error_message):
        self.send_response(400)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {
                    "error_message": error_message
                 }
            ).encode('utf-8')
        )

    def __read_body(self):
        content_len = int(self.headers.get('Content-Length'))
        body = self.rfile.read(content_len)
        return json.loads(body.decode('utf-8'))

    @staticmethod
    def print_help(host_name, server_port):
        url = f"http://{host_name}:{server_port}"
        print(f"Server started {url}\n"
              "Supported endpoints:\n"
              f"GET \t{url}/authorization-url - get authorization url\n"
              f"GET \t{url}/list - get list of twits for the last 24 hours\n"
              f"GET \t{url}/list?time=<time> - get list of twits for the 24 hours before time if it's a time, and for this date if it's a date\n"
              f"GET \t{url}/list/html - get list of twits for the last 24 hours as html\n"
              f"GET \t{url}/list/html?time=<time> - get list of twits for the 24 hours before time if it's a time as html\n"
              f"POST \t{url}/start - start server\n"
              f"POST \t{url}/stop - stop server\n"
              f"GET \t{url}/status - get server status\n"
              )


