# -*- coding: utf-8 -*-
from jpwp.settings import *
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


class RequestParser:
    """
    Object responsible for new requests processing.
    """

    N = 8  # dimension for sub-images matrix, possible values: 4/8/16/32 (currently only 8 is stored in db)

    def __init__(self, request, db):
        """
        Initializes parser object.

        Processes request's content parsing to automatically call methods with suitable arguments.
        First separates methods names from their arguments into separate lists.
        Then calls saved methods by name one by one, stopping if an error occurs.
        Finally sets status code accordingly to the processing result.

        :param request: request dictionary
        :param db: db handle
        """
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
        """
        Gets Wikipedia's page text content along with the country's flag.
        :param name: country name
        :return: page text, country flag
        """

        page = requests.get(WIKI_TEXT_URL+name)
        if page.status_code == 404:
            self.status = 404
            return None, None

        soup = BeautifulSoup(page.content, 'html.parser')

        try:
            flag = [f.find('img') for f in soup.find_all('a', title=re.compile(r'Flag of.*')) if f.find('img') is not None][0]['src']
            flag = flag[2:]
        except IndexError:  # no flag picture on the page
            flag = None

        # getting rid of unnecessary stuff
        content = soup.find('div', {'id': 'mw-content-text'})
        [c.extract() for c in content.find_all(attrs={'class': ['hatnote', 'metadata', 'toc', 'infobox', 'thumb', 'reference', 'reflist', 'external', 'noprint', 'navbox']})]
        [c.extract() for c in content.find_all(attrs={'id': ['coordinates']})]

        # further filtering, converting and formatting data
        text = ''.join([x.string for x in content.findAll(text=True)])
        text = text[:text.find('References')]
        text = re.sub(r'[\n]{3,}','\n\n', text).strip()

        self.status = 200
        return text, flag

    def country(self, name):
        """
        Gets country information stored in object properties.
        Saves both text content and flag image url.
        Sets the status code to 404 when there is no such country as the given one.
        Should always be called as the first method for text data processing.
        :param name: country name
        """
        self.data, self.flag = self.get_content(name)

    def tag(self, tag):
        """
        Filteres previously saved text data. Picks only sentences that contain given tag.
        Sets the status code to 400 when there is no data to be filtered, eg. someone called 'tag()' before 'country()'.
        Leads to setting status code to 404 when no sentence was found.
        :param tag: tag to find
        """
        try:
            self.data = re.findall(r'\w?[^.?!]*{0}[^.?!]*[.?!]'.format(tag), self.data)
            if len(self.data) == 0:
                self.data = None
        except TypeError:
            self.status = 400

    def getFlag(self):
        """
        Sets data property to the flag url.
        Leads to setting status code to 404 if no flag was found on the page.
        """
        self.data = self.flag

    def checkFlag(self, link):
        """
        Recognises flag given as image url.

        First downloads image from the link. Then splits image into 8x8 (actually 64x1) matrix of smaller parts.
        For each part histogram is calculated and normalized.
        After that given histograms matrix is compared against a set of corresponding matrixes stored in db for each
        country.
        If the mean value of correlation between histograms is greater or equal 0.99, the country is considered to be
        matched. Data property is set to a country's name.

        :param link: flag image url
        """
        # downloading image
        result = requests.get(link, stream=True)
        if result.status_code == 404:
            self.status = 404
            self.data = None
            return
        img = Image.open(StringIO(result.content))
        img.save('img.png')
        img = cv2.imread('img.png',0)

        # splitting image into smaller parts
        r, c = img.shape[:2]
        dr, dc = r/RequestParser.N, c/RequestParser.N
        sub_imgs = [img[y*dr:(y+1)*dr, x*dc:(x+1)*dc] for x in range(RequestParser.N) for y in range(RequestParser.N)]

        # calculating histograms
        sub_hists = map(lambda i: cv2.calcHist(i, [0, 1, 2], None, [8, 8, 8],[0, 256, 0, 256, 0, 256]), sub_imgs)
        sub_hists = map(lambda x: cv2.normalize(x).flatten(), sub_hists)
        sub_hists = numpy.array(sub_hists)

        result = 0
        country_name = None
        self.status = 404

        # comparing histograms against those stored in db
        for r in self.db.flags.find():
            sub_hists_db = list(numpy.float32(r['subhistograms{}'.format(RequestParser.N)]))
            sub_result = [cv2.compareHist(h1, h2, cv2.cv.CV_COMP_CORREL) for h1,h2 in zip(sub_hists, sub_hists_db)]
            sub_result = min(sub_result) # sum(sub_result)/len(sub_result)
            if sub_result > result:
                result = sub_result
                country_name = r['country']
                self.status = 200
                if result >= 0.99:
                    break

        self.data = country_name


class RequestHandler(tornado.web.RequestHandler):
    """
    Tornado web server request handler.
    """

    def get(self):
        """
        Handles GET request.
        Serves concise note if the server is up and running.
        """
        self.write('OK')

    def post(self):
        """
        Handles POST requests and serves content accordingly to the result.
        First loads request body as json for further processing. If it fails, sends 'Bad request' response to user. If not,
        'fixes' request content.
        Then the database connection is established, and the exact same request is being searched. If the request was found,
        it's data is served and if not, any request with that data content is being searched and saved if it succeeds.
        If no data was found, request is passed to RequestParser, which handles new requests processing. If parser returns
        with an error status code, error is served to user. Otherwise processed request data is served and stored in db.
        """
        def fix_content():
            """
            Fixes request's content if necessary. Adds semicolon between methods to separate them. Also replaces
            spaces with underscores.
            """
            request['content'] = re.sub(r'\)(?=[^;])', r');', request['content']) # adding delimeter
            request['content'] = re.sub(r'\s', r'_', request['content']) # replacing spaces

        try:
            request = json.loads(self.request.body)
        except ValueError:
            self.send_error(400)
            return
        fix_content()

        # establishing db connection
        conn = pymongo.MongoClient(DB_ADDRESS)
        db = conn[DB_NAME]
        db.authenticate(DB_USER, DB_PASS)

        # searching for exact same request in db
        db_result_req = db.requests.find_one(request)
        if not db_result_req:
            # searching for similar request
            data = dict(content=request['content'], type=request['type'])
            db_result_data = db.data.find_one(data)
            if not db_result_data:
                # processing new request
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

            # saving request after successful processing
            db.requests.insert_one(request)
        else:
            db_result_data = db.data.find_one({'_id': db_result_req['data_id']})
            print '[REQ DB]'
            self.write(json.dumps(db_result_data['data'], ensure_ascii=False).encode('utf-8'))


if __name__ == "__main__":
    # app and server initialization
    application = tornado.web.Application([
        (r"/", RequestHandler)
    ])

    server = tornado.httpserver.HTTPServer(application)
    server.bind(SERVER_PORT, address=SERVER_ADDRESS)
    server.start(0)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()
