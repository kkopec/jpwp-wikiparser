# -*- coding: utf-8 -*-
from jpwp.helpers import *
from jpwp.settings import *
from bs4 import BeautifulSoup
from random import randint
import json
import re
import requests

# Sample requests
requests_list = [
    dict(address=SERVER_ADDRESS, port=SERVER_PORT, type='text', content='country(Poland)'),
    dict(address=SERVER_ADDRESS, port=SERVER_PORT, type='text', content='country(Poland)tag(Sea)'),
    dict(address=SERVER_ADDRESS, port=SERVER_PORT, type='text', content='country(Poland)getFlag'),
    dict(address=SERVER_ADDRESS, port=SERVER_PORT, type='image', content='checkFlag(https://upload.wikimedia.org/wikipedia/en/thumb/1/12/Flag_of_Poland.svg/800px-Flag_of_Poland.svg.png)')
]


def get_random_request():
    """
    Creates random request.
    """

    method_id = randint(0,len(METHODS)-1)
    method = METHODS[method_id]
    type = 'text'
    if method_id in [0,2]:
        method = method.format(COUNTRIES[randint(0,len(COUNTRIES)-1)])
    elif method_id == 1:
        method = method.format(COUNTRIES[randint(0,len(COUNTRIES)-1)], TAGS[randint(0,len(TAGS)-1)])
    else:
        flag = None
        while flag is None:
            ctr = COUNTRIES[randint(0,len(COUNTRIES)-1)]
            cou = re.sub(r'\s',r'_',ctr)
            page = requests.get(WIKI_FLAG_URL.format(cou))
            soup = BeautifulSoup(page.content, 'html.parser')
            try:
                flag = soup.find_all('img', alt=re.compile(r'Flag of (.*)?{}'.format(ctr)))[0]['src']
                flag = 'http:'+flag
                flag = re.sub(r'\d+(?=px-Flag)', r'800',flag)
            except IndexError:
                flag = None

        method = method.format(flag)
        type = 'image'

    return dict(address=SERVER_ADDRESS, port=SERVER_PORT, type=type, content=method)

if __name__ == "__main__":
    print '\nSending requests...\n'

    for n in range(REQUESTS_NUMBER):
        requests_list.append(get_random_request())

    headers = {'content-type': 'application/json'}
    for req in requests_list:
        r = requests.post('http://{0}:{1}'.format(SERVER_ADDRESS, SERVER_PORT), data=json.dumps(req), headers=headers)
        print '\n',r.status_code,' - ',req['content']
        print r.content[:300] # screen flood prevention
