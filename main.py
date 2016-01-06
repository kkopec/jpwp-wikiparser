#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import requests
import pymongo
from bs4 import BeautifulSoup

import sys

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

WIKI_URL = 'http://en.wikipedia.org/wiki/'

DB_ADDRESS = 'mongodb://mongo0.mydevil.net:27017'
DB  = 'mo11939_jpwp'
DBU = 'mo11939_jpwp'
DBP = 'TI3jpwp'


class RequestParser:
    def __init__(self, request):
        self.data = None
        self.flag = None
        self.meth_list = []
        self.args_list = []

        request['content'] = re.sub(r'\)(?=[^;])', r');', request['content']) # adding delimeter

        for command in request['content'].split(';'):
            parts = command.split('(')

            if len(parts) == 1:
                parts.append(None)
            else:
                parts[1] = parts[1][:-1]

            self.meth_list.append(parts[0])
            self.args_list.append(parts[1])

        print >> sys.stderr, self.meth_list
        print >> sys.stderr, self.args_list

        for m, a in zip(self.meth_list, self.args_list):
            method = getattr(self, m)
            if not method:
                continue
            method(a) if a is not None else method()

    @staticmethod
    def get_content(page):
        soup = BeautifulSoup(page.content, 'html.parser')

        flag = [f.find('img') for f in soup.find_all('a', title=re.compile(r'Flag of.*')) if f.find('img') is not None][0]['src']
        flag = flag[2:]

        content = soup.find('div', {'id': 'mw-content-text'})
        [c.extract() for c in content.find_all(attrs={'class': ['hatnote', 'metadata', 'toc', 'infobox', 'thumb', 'reflist', 'external', 'noprint', 'navbox']})]
        [c.extract() for c in content.find_all(attrs={'id': ['coordinates']})]

        text = ''.join([x.string for x in content.findAll(text=True)])
        text = text[:text.find('References')]
        text = re.sub(r'[\n]{3,}','\n\n', text).strip()

        return text, flag

    def country(self, name):
        page = requests.get(WIKI_URL+name)
        self.data, self.flag = self.get_content(page)

    def tag(self, tag):
        self.data = re.findall(r'[:upper:][^.?!]*{0}[^.?!]*[.?!]'.format(tag), self.data)

    def getFlag(self):
        self.data = self.flag

    def checkFlag(self, link):
        self.data = link


class RequestHandler(tornado.web.RequestHandler):
    def get(self):
        headers = {'content-type': 'application/json'}
        data = {
            'address': 'localhost',
            'port': '9901',
            'type': 'text',
            'content': 'country(Poland)getFlag'
        }
        r = requests.post('http://localhost:9901', params=data, headers=headers)
        print r.status_code

        self.write('ok')

    def post(self):
        data = {
            'address': self.get_argument("address", default="localhost", strip=True),
            'port':    self.get_argument("port", default="9901", strip=True),
            'type':    self.get_argument("type", None, True),
            'content': self.get_argument("content", None, True)
        }

        conn = pymongo.MongoClient(DB_ADDRESS)
        conn[DB].authenticate(DBU, DBP)
        db = conn[DB]

        dbf_result = db.requests.find_one(data)
        if not dbf_result:
            result = RequestParser(data)
            print result.data
            dbi_result = db.requests.insert_one(data).inserted_id
        else:
            print 'find in db'


if __name__ == "__main__":
    print '\n\n\n'
    application = tornado.web.Application([
        (r"/", RequestHandler)
    ])

    server = tornado.httpserver.HTTPServer(application)
    server.bind(9901)
    server.start(0)  # Forks multiple sub-processes
    tornado.ioloop.IOLoop.current().start()

    # http_server = tornado.httpserver.HTTPServer(application)
    # http_server.listen(options.port)
    # tornado.ioloop.IOLoop.current().start()



# def parse_request(request):
#     request['content'] = re.sub(r'\)(?=[^;])', r');', request['content']) # adding delimeter
#
#     methods = []
#     commands = request['content'].split(';')
#
#     for command in commands:
#         parts = command.split('(')
#
#         if len(parts) == 1:
#             parts.append(None)
#         else:
#             parts[1] = parts[1][:-1]
#
#         methods.append({'name':parts[0],'arguments':parts[1]})
#
#     methods = sorted(methods, key=lambda k: k['name']) # sorting
#
#     possibles = globals().copy()
#     possibles.update(locals())
#     for m in methods:
#         method = possibles.get(m['name'])
#         if not method:
#             raise Exception("Method %s not implemented" % m['name'])
#         method(m['arguments'])
#     return 0