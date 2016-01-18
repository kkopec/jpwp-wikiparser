# -*- coding: utf-8 -*-
from jpwp.helpers import *
from jpwp.settings import *
from bs4 import BeautifulSoup
from PIL import Image
from StringIO import StringIO
import cv2
import numpy
import pymongo
import re
import requests

if __name__ == "__main__":
    conn = pymongo.MongoClient(DB_ADDRESS)
    db = conn[DB_NAME]
    db.authenticate(DB_USER, DB_PASS)

    for ctr in COUNTRIES:
        cou = re.sub(r'\s',r'_',ctr)
        page = requests.get(WIKI_FLAG_URL.format(cou))
        soup = BeautifulSoup(page.content, 'html.parser')
        try:
            flag = soup.find_all('img', alt=re.compile(r'Flag of (.*)?{}'.format(ctr)))[0]['src']
            flag = 'http:'+flag
            flag = re.sub(r'\d+(?=px-Flag)', r'800',flag)
        except IndexError:
            print 'No flag for '+ctr
            continue

        result = requests.get(flag, stream=True)
        img = Image.open(StringIO(result.content))
        img.save('img.png')
        img = cv2.imread('img.png',0)

        obj = {'country': ctr}

        r, c = img.shape[:2]

        for N in MATRIX_N:
            dr, dc = r/N, c/N

            sub_imgs = [img[y*dr:(y+1)*dr, x*dc:(x+1)*dc] for x in range(N) for y in range(N)]
            sub_hists = map(lambda i: cv2.calcHist(i, [0, 1, 2], None, [8, 8, 8],[0, 256, 0, 256, 0, 256]), sub_imgs)
            sub_hists = map(lambda x: cv2.normalize(x).flatten(), sub_hists)

            obj['subhistograms{}'.format(N)] = numpy.array(sub_hists).tolist()

        ins = db.flags.insert_one(obj).inserted_id
        print ctr, ' - ', ins
