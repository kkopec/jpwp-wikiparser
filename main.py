#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pymongo

WIKI_URL = 'http://en.wikipedia.org/wiki/'

DB_ADDRESS = 'mongodb://mongo0.mydevil.net:27017'
DB  = 'mo11939_jpwp'
DBU = 'mo11939_jpwp'
DBP = 'TI3jpwp'


def get_country_info(country):
    return requests.get(WIKI_URL+country)


#def get_content(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    #for para in soup.find_all('p'):
        #print(para.get_text().encode('ascii','ignore'))


if __name__ == "__main__":
    page = get_country_info('Poland')
    #get_content(page)

    conn = pymongo.MongoClient(DB_ADDRESS)
    is_connected = conn[DB].authenticate(DBU,DBP)
    db = conn[DB]

    data = {
        'address': 'localhost',
        'port': '9091',
        'type': 'text',
        'content': 'country(Poland)'
    }

    result = db.requests.insert_one(data).inserted_id

    print result
