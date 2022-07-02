import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

resource_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
env = Environment(loader=FileSystemLoader(resource_directory))


class HtmlGenerator:
    def __init__(self):
        self._page_template = env.get_template('twits_page_template.j2')
        self._twit_template = env.get_template('twit_template.j2')

    def render(self, twits, date_time: datetime):
        users = twits['includes']['users']
        table_content = ""
        for twit in reversed(twits['data']):
            author_object = next((x for x in users if x['id'] == twit['author_id']), None)
            author_name = author_object['name']
            author_profile_image_url = author_object['profile_image_url']
            table_content = table_content + self._twit_template.render(text=twit['text'],
                                                                       author_name=author_name,
                                                                       author_profile_image_url=author_profile_image_url,
                                                                       created_at=twit['created_at'])
        return self._page_template.render(date_time=date_time.isoformat(), table_content=table_content)
