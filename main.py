#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import json
import pymongo
import re
import requests

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

WIKI_URL = 'http://en.wikipedia.org/wiki/'

DB_ADDRESS = 'mongodb://mongo0.mydevil.net:27017'
DB_NAME    = 'mo11939_jpwp'
DB_USER    = 'mo11939_jpwp'
DB_PASS    = 'TI3jpwp'

SERVER_ADDRESS = 'localhost'
SERVER_PORT    = '9901'


class RequestParser:
    def __init__(self, request):
        self.data = None
        self.flag = None
        self.status = 200
        self.meth_list = []
        self.args_list = []

        # parsing request content
        for command in request['content'].split(';'):
            parts = command.split('(')

            if len(parts) == 1:
                parts.append(None)
            else:
                parts[1] = parts[1][:-1] # getting rid of closing bracket

            self.meth_list.append(parts[0])
            self.args_list.append(parts[1])

        # invoking methods
        for m, a in zip(self.meth_list, self.args_list):
            if self.status != 200:
                return

            try:
                method = getattr(self, m)
            except AttributeError:
                self.status = 400
                return
            method(a) if a is not None else method()

        self.status = 200 if self.data is not None else 404

    def get_content(self, name):
        page = requests.get(WIKI_URL+name)
        if page.status_code == 404:
            self.status = 404
            return None, None

        soup = BeautifulSoup(page.content, 'html.parser')

        try:
            flag = [f.find('img') for f in soup.find_all('a', title=re.compile(r'Flag of.*')) if f.find('img') is not None][0]['src']
            flag = flag[2:]
        except IndexError:
            flag = None

        content = soup.find('div', {'id': 'mw-content-text'})
        [c.extract() for c in content.find_all(attrs={'class': ['hatnote', 'metadata', 'toc', 'infobox', 'thumb', 'reference', 'reflist', 'external', 'noprint', 'navbox']})]
        [c.extract() for c in content.find_all(attrs={'id': ['coordinates']})]

        text = ''.join([x.string for x in content.findAll(text=True)])
        text = text[:text.find('References')]
        text = re.sub(r'[\n]{3,}','\n\n', text).strip()

        self.status = 200
        return text, flag

    def country(self, name):
        self.data, self.flag = self.get_content(name)

    def tag(self, tag):
        try:
            self.data = re.findall(r'\w[^.?!]*{0}[^.?!]*[.?!]'.format(tag), self.data)
            if len(self.data) == 0:
                self.data = None
        except TypeError:
            self.status = 400

    def getFlag(self):
        self.data = self.flag

    def checkFlag(self, link):
        self.data = link


class RequestHandler(tornado.web.RequestHandler):
    def get(self):
        headers = {'content-type': 'application/json'}
        data = dict(address=SERVER_ADDRESS, port=SERVER_PORT, type='text', content='country(Poland)getFlag')
        r = requests.post('http://{0}:{1}'.format(SERVER_ADDRESS, SERVER_PORT), data=json.dumps(data), headers=headers)
        print r.status_code

        self.write('{0}'.format(r.status_code))

    def post(self):
        def fix_content():
            request['content'] = re.sub(r'\)(?=[^;])', r');', request['content']) # adding delimeter
            request['content'] = re.sub(r'\s', r'_', request['content']) # replacing spaces

        try:
            request = json.loads(self.request.body)
        except ValueError:
            self.send_error(400)
            return

        fix_content()

        conn = pymongo.MongoClient(DB_ADDRESS)
        db = conn[DB_NAME]
        db.authenticate(DB_USER, DB_PASS)

        db_result_req = db.requests.find_one(request)
        if not db_result_req:
            data = {
                'content': request['content'],
                'type':    request['type']
            }
            db_result_data = db.data.find_one(data)
            if not db_result_data:
                result = RequestParser(request)
                if result.status == 404:
                    self.send_error(404)
                    return
                elif result.status == 400:
                    self.send_error(400)
                    return
                data['data'] = result.data
                db_result_in = db.data.insert_one(data).inserted_id
                request['data_id'] = db_result_in
                print '[NEW DATA]'
                self.write(json.dumps(result.data, ensure_ascii=False).encode('utf-8'))
                self.set_status(201)
            else:
                request['data_id'] = db_result_data['_id']
                print '[DATA DB]'
                self.write(json.dumps(db_result_data['data'], ensure_ascii=False).encode('utf-8'))

            db.requests.insert_one(request)
        else:
            db_result_data = db.data.find_one({'_id': db_result_req['data_id']})
            print '[REQ DB]'
            self.write(json.dumps(db_result_data['data'], ensure_ascii=False).encode('utf-8'))


if __name__ == "__main__":
    print '\n\n'
    application = tornado.web.Application([
        (r"/", RequestHandler)
    ])

    server = tornado.httpserver.HTTPServer(application)
    server.bind(SERVER_PORT)
    server.start(0)  # Forks multiple sub-processes
    tornado.ioloop.IOLoop.current().start()