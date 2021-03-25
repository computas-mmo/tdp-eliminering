import logging
import time
from multiprocessing import Pool
from typing import List
import sys

import requests

logger = logging.getLogger('confluence_api')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('confluence_api.log')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


class ConfluenceAPI:
    # FIXME: Change base-url depending on which server you're running on (test or not)
    base_url = 'https://confluencetest.computas.com'

    def __init__(self, space, *, username, password):
        self.auth = (username, password)
        self.space = space
        logger.info(f'Initialized API for client: [{self.base_url}]')

    def __repr__(self):
        return f'ConfluenceAPI<{self.space}>'

    def init_scrape_url(self):
        return f'/rest/api/content?spaceKey={self.space}&limit=500&start=0&type=page'

    def get_pages_in_space(self) -> list:
        pages = []
        next_page_url = self.init_scrape_url()
        while next_page_url is not None:
            logger.info(f'Currently scraping spaces from: {next_page_url}')
            response = requests.get(ConfluenceAPI.base_url + next_page_url, auth=self.auth).json()
            pages.extend(response['results'])
            next_page_url = response['_links'].get('next')
            time.sleep(1)  # rate limiter just in case ¯\_(ツ)_/¯
        return pages

    def get_expanded_body(self, page: dict):
        page_id = page['id']
        page_title = page['title']
        logger.info(f'Requesting expanded body for [{page_id} - {page_title}]')

        time.sleep(0.01)  # rate limiter just in case ¯\_(ツ)_/¯
        return requests.get(
            url=f'{ConfluenceAPI.base_url}/rest/api/content/{page_id}',
            params={'expand': 'body.storage,version,space'},
            auth=self.auth
        ).json()

    def get_expanded_bodies(self, pages: List[dict]):
        with Pool(processes=6) as pool:
            expanded_pages = pool.map(self.get_expanded_body, pages)
        return expanded_pages

    def update_page_body(self, page, body):
        page_id = page['id']
        page_title = page['title']

        logger.info(f'Updating [{page_id} - {page_title}]')

        requests.put(
            url=f'{ConfluenceAPI.base_url}/rest/api/content/{page_id}',
            headers={'Content-Type': 'application/json'},
            auth=self.auth,
            json={
                "id": page_id,
                "type": page['type'],
                "title": page_title,
                "space": {"key": page['space']['key']},
                "body": {
                    "storage": {
                        "value": body,
                        "representation": "storage"
                    }
                }, "version": {
                    "number": page['version']['number'] + 1
                }
            }
        )
