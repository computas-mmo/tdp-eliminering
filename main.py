import argparse
import logging
import pickle
import re
from bs4 import BeautifulSoup
from multiprocessing import Pool
from pathlib import Path
from pprint import pprint
from typing import Optional

from confluence import ConfluenceAPI
from regex import FRAGMENT_INCLUDE_REPLACE, FRAGMENT_INCLUDE_SEARCH, FRAGMENT_REPLACE, FRAGMENT_SEARCH

logger = logging.getLogger('confluence_api')

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', type=str, help='Confluence username', required=True)
parser.add_argument('-p', '--password', type=str, help='Confluence password', required=True)
parser.add_argument('-s', '--spaces', nargs='+', help='List of spaces to migrate micros', required=True)
parser.add_argument('-m', '--method', type=str, help='Method for search / replace', choices={'regex', 'xml'},
                    required=True, default='xml')

args = parser.parse_args()

# global constant instead of duplicating literals
PARAMETER = 'ac:parameter'
NAME = 'ac:name'


def process_page_regex(page) -> Optional[str]:
    body = page['body']['storage']['value']

    new_body = re.sub(FRAGMENT_SEARCH, FRAGMENT_REPLACE, body)
    new_body = re.sub(FRAGMENT_INCLUDE_SEARCH, FRAGMENT_INCLUDE_REPLACE, new_body)

    return None if new_body == body else new_body


def process_page_xml(page) -> Optional[str]:
    body = page['body']['storage']['value']
    soup = BeautifulSoup(body, features='html.parser')

    diff = False
    # TDP Fragment -> MultiExcerpt Macro
    for macro in soup.find_all(name='ac:structured-macro', attrs={NAME: 'tdp-fragment'}):
        macro[NAME] = 'multiexcerpt'
        macro.find(PARAMETER, attrs={NAME: 'key'})[NAME] = 'MultiExcerptName'

        diff = True

    # TDP Fragment Include -> MultiExcerpt Include Macro
    for macro in soup.find_all(name='ac:structured-macro', attrs={NAME: 'tdp-fragment-include'}):
        macro[NAME] = 'multiexcerpt-include'
        macro.find(PARAMETER, attrs={NAME: 'key'})[NAME] = 'MultiExcerptName'

        # Optional panel argument for multiexcerpt-include-macro
        panel = macro.find(PARAMETER, attrs={NAME: 'panel'})
        if panel is not None:
            panel[NAME] = 'addpanel'

        # Remove all other arguments
        for option in ('header', 'pagecontext', 'text', 'searchable', 'expandrelative'):
            for tag in macro.find_all(PARAMETER, attrs={NAME: option}):
                tag.decompose()

        diff = True

    """
    =Skriptbytte makroer:

    ==tdp-incoming-links => incoming-links
    Må sjekke parameterne, men ellers ok. Potensielt bare bytte navn.

    ==tdp-page-status => status
    Ideelt sett: Bytte med Status macro. Det finnes et kommentarfelt som bør ses på å beholde innholdet i.

    ==tdp-pagepropertiesreport => pagepropertiesreport
    Ta med Ancestor, label, in space, og 'columns to show' om det ikke er mulig å bare få med alle

    ==tdp-div => div Merk: for sideposisjonering
    Høyre eller midstilt tekst skal beholdes. Noprint skal ignoreres, her skal selve makroen fjenres men innholdet beholdes.
    Potensielt best å bare gjøre alt i skriptbytte, fremfor å ta med en skriptfjerningsmodul også her.

    =Skriptfjerne makroer:

    ==tdp-div MERK: For noprint, ikke for tekststilling! Potensielt ikke med i denne listen. Se over.

    ==tdp-comment 

    ==tdp-template-header

    ==tdp-subpage-list

    ==tdp-add-page-from-template-description

    ==tdp-predefined-search
    """

    return soup.decode_contents() if diff else None


def init_data(space: str, api: ConfluenceAPI):
    """
    TODO: This saves a snapshot of the spaces locally and is mostly used for development.
        Make sure that the pages are up-to-date when running it on the live-server
    """
    logger.info(f'Downloading pages for [{space}]')
    expanded_pages_path = Path('cache') / f'{space}.p'

    if expanded_pages_path.exists():
        with open(expanded_pages_path, 'rb') as f:
            expanded_pages = pickle.load(f)
    else:
        pages = api.get_pages_in_space()
        expanded_pages = api.get_expanded_bodies(pages)

        with open(expanded_pages_path, 'wb') as f:
            pickle.dump(expanded_pages, f)

    return expanded_pages


def migrate_macros(space: str, username: str, password: str, callback_func: callable):
    # TODO: Should use service-account or another type of authentication
    confluence_api = ConfluenceAPI(space, username=username, password=password)
    expanded_pages = init_data(space, confluence_api)

    logger.info(f'Starting update process for [{space}]')
    with Pool(processes=6) as pool:
        formatted_bodies = pool.map(callback_func, expanded_pages)

        for page, body in zip(expanded_pages, formatted_bodies):
            if body is None:
                continue
            confluence_api.update_page_body(page, body)


if __name__ == '__main__':

    # if args.method == 'xml':
    #     callback = process_page_xml
    # elif args.method == 'regex':
    #     callback = process_page_regex
    # else:
    #     raise ValueError(f'Invalid method: [{args.method}]')

    # Just defaulting to xml for now
    callback = process_page_xml

    for space in args.spaces:
        migrate_macros(space, username=args.username, password=args.password, callback_func=callback)
