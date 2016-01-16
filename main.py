#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from PIL import Image
from StringIO import StringIO
import cv2
import json
import numpy
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
    N = 8 # 4/8/16/32

    def __init__(self, request, db):
        self.data = None
        self.flag = None
        self.status = 200
        self.db = db
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
        result = requests.get(link, stream=True)
        img = Image.open(StringIO(result.content))
        img.save('img.png')
        img = cv2.imread('img.png',0)

        r, c = img.shape[:2]
        dr, dc = r/RequestParser.N, c/RequestParser.N

        sub_imgs = [img[y*dr:(y+1)*dr, x*dc:(x+1)*dc] for x in range(RequestParser.N) for y in range(RequestParser.N)]
        sub_hists = map(lambda i: cv2.calcHist(i, [0, 1, 2], None, [8, 8, 8],[0, 256, 0, 256, 0, 256]), sub_imgs)
        sub_hists = map(lambda x: cv2.normalize(x).flatten(), sub_hists)

        sub_hists = numpy.array(sub_hists)

        result = 0
        country_name = []
        self.status = 404

        for r in self.db.flags.find():
            sub_hists_db = list(numpy.float32(r['subhistograms{}'.format(RequestParser.N)]))
            sub_result = [cv2.compareHist(h1, h2, cv2.cv.CV_COMP_CORREL) for h1,h2 in zip(sub_hists, sub_hists_db)]
            sub_result = sum(sub_result)/len(sub_result)
            if sub_result > result:
                result = sub_result
                country_name = [r['country']]
                self.status = 200
                if result >= 0.99:
                    break
            elif sub_result == result:
                country_name.append(r['country'])
        if len(country_name) == 0:
            country_name = None

        self.data = country_name


class RequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('OK')

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
                result = RequestParser(request, db)
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
    server.stop()
    server.bind(SERVER_PORT, address=SERVER_ADDRESS)
    server.start(0)  # Forks multiple sub-processes
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()
