#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from PIL import Image
from StringIO import StringIO
import numpy
import cv2
import pymongo
import re
import requests
import sys

WIKI = 'https://en.wikipedia.org/wiki/File:Flag_of_{0}.svg'
DB_ADDRESS = 'mongodb://mongo0.mydevil.net:27017'
DB_NAME    = 'mo11939_jpwp'
DB_USER    = 'mo11939_jpwp'
DB_PASS    = 'TI3jpwp'

MATRIX_N = [8]

countries = [
    'Afghanistan',    'Albania',    'Algeria',    'Andorra',    'Angola',    'Antigua and Barbuda',    'Argentina',
    'Armenia',    'Australia',    'Austria',    'Azerbaijan',

    'Bahamas',    'Bahrain',    'Bangladesh',    'Barbados',    'Belarus',    'Belgium',    'Belize',    'Benin',
    'Bhutan',    'Bolivia',    'Bosnia and Herzegovina',    'Botswana',    'Brazil',    'Brunei',    'Bulgaria',
    'Burkina Faso',    'Burundi',

    'Cambodia',    'Cameroon',    'Canada',    'Cape Verde',    'Central African Republic',    'Chad',    'Chile',
    'China',    'Colombia',    'Comoros',    'Costa Rica',    'Croatia',    'Cuba',    'Cyprus',
    'Czech Republic',

    'Democratic Republic of the Congo',    'Denmark',    'Djibouti',    'Dominica',    'Dominican Republic',

    'East Timor',    'Ecuador',    'Egypt',    'El Salvador',    'Equatorial Guinea',    'Eritrea',    'Estonia',
    'Ethiopia',

    'Federated States of Micronesia',    'Fiji',    'Finland',    'France',

    'Gabon',    'Gambia',    'Georgia',    'Germany',    'Ghana',    'Greece',    'Grenada',    'Guatemala',
    'Guinea',    'Guinea-Bissau',    'Guyana',

    'Haiti',    'Honduras',    'Hungary',

    'Iceland',    'India',    'Indonesia',    'Iran',    'Iraq',    'Ireland',    'Israel',    'Italy',    'Ivory Coast',

    'Jamaica',    'Japan',    'Jordan',

    'Kazakhstan',    'Kenya',    'Kiribati',    'Kuwait',    'Kyrgyzstan',

    'Laos',    'Latvia',    'Lebanon',    'Lesotho',    'Liberia',    'Libya',    'Liechtenstein',    'Lithuania',
    'Luxembourg',

    'Macedonia',    'Madagascar',    'Malawi',    'Malaysia',    'Maldives',    'Mali',    'Malta',    'Marshall Islands',
    'Mauritania',    'Mauritius',    'Mexico',    'Moldova',    'Monaco',    'Mongolia',    'Montenegro',    'Morocco',
    'Mozambique',    'Myanmar',

    'Namibia',    'Nauru',    'Nepal',    'Netherlands',    'New Zealand',    'Nicaragua',    'Niger',    'Nigeria',
    'Norway',    'North Korea',

    'Oman',

    'Palestine',    'Pakistan',    'Palau',    'Panama',    'Papua New Guinea',    'Paraguay',    'Peru',
    'Philippines',    'Poland',    'Portugal',

    'Qatar',

    'Republic of the Congo',    'Romania',    'Russia',    'Rwanda',

    'Saint Kitts and Nevis',    'Saint Lucia',    'Saint Vincent and the Grenadines',    'Samoa',    'San Marino',
    'Sao Tome and Principe',    'Saudi Arabia',    'Senegal',    'Serbia',    'Seychelles',    'Sierra Leone',
    'Singapore',    'Slovakia',    'Slovenia',    'Solomon Islands',    'Somalia',    'South Africa',    'South Korea',
    'South Sudan',    'Spain',    'Sri Lanka',    'Sudan',    'Suriname',    'Swaziland',
    'Sweden',    'Switzerland',    'Syria',

    'Tajikistan',    'Tanzania',    'Thailand',    'Togo',    'Tonga',    'Trinidad and Tobago',    'Tunisia',
    'Turkey',    'Turkmenistan',    'Tuvalu',

    'Uganda',    'Ukraine',    'United Arab Emirates',    'United Kingdom',    'United States',    'Uruguay',
    'Uzbekistan',

    'Vanuatu',    'Vatican City',    'Venezuela',    'Vietnam',

    'Yemen',

    'Zambia',    'Zimbabwe'
]


if __name__ == "__main__":
    conn = pymongo.MongoClient(DB_ADDRESS)
    db = conn[DB_NAME]
    db.authenticate(DB_USER, DB_PASS)

    for ctr in countries:
        cou = re.sub(r'\s',r'_',ctr)
        page = requests.get(WIKI.format(cou))
        soup = BeautifulSoup(page.content, 'html.parser')
        try:
            flag = soup.find_all('img', alt=re.compile(r'Flag of (.*)?{}'.format(ctr)))[0]['src']
            flag = 'http:'+flag
            flag = re.sub(r'\d+(?=px-Flag)', r'800',flag)
        except IndexError:
            print sys.stderr, 'No flag for '+ctr
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
