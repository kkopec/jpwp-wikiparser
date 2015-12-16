#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

WIKI_URL = 'http://en.wikipedia.org/wiki/'


def get_country_info(country):
    return requests.get(WIKI_URL+country)


def get_content(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    for para in soup.find_all('p'):
        print(para.get_text().encode('ascii','ignore'))


if __name__ == "__main__":
    page = get_country_info('Poland')
    get_content(page)