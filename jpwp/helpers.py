# -*- coding: utf-8 -*-
"""
Settings for helper scripts.
"""
# Wikipedia flag url
WIKI_FLAG_URL = 'https://en.wikipedia.org/wiki/File:Flag_of_{0}.svg'

# Client settings
REQUESTS_NUMBER = 10
METHODS = [
    'country({0})',
    'country({0})tag({1})',
    'country({0})getFlag',
    'checkFlag({0})',
]

# Histograms matrix dimension
MATRIX_N = [8] # histograms matrix dimension

# Countries list
COUNTRIES = [
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

# Sample tags list
TAGS = [
    "Dynasty",
    "Empire",
    "Freedom",
    "Independence",
    "Kingdom",
    "River",
    "Sea",
    "Union",
    "War",
    "ThereIsNoSuchTag"
]

# Sample image urls
IMG_URLS = [
    'https://upload.wikimedia.org/wikipedia/en/thumb/1/12/Flag_of_Poland.svg/800px-Flag_of_Poland.svg.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Saint_Lucia.svg/800px-Flag_of_Saint_Lucia.svg.png',
    'https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Flag_of_Spain.svg/750px-Flag_of_Spain.svg.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Tuvalu.svg/800px-Flag_of_Tuvalu.svg.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Flag_of_Zimbabwe.svg/800px-Flag_of_Zimbabwe.svg.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Flag_of_Yemen.svg/450px-Flag_of_Yemen.svg.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/492px-Flag_of_Nepal.svg.png',
    'https://upload.wikimedia.org/wikipedia/en/thumb/c/c3/Flag_of_France.svg/800px-Flag_of_France.svg.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Flag_of_Kiribati.svg/600px-Flag_of_Kiribati.svg.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Andorra.svg/800px-Flag_of_Andorra.svg.png',
    'https://upload.wikimedia.org/wikipedia/en/thumb/f/f3/Flag_of_Russia.svg/800px-Flag_of_Russia.svg.png'
]
