import csv

import sys
from urllib.parse import urljoin

import requests

f = csv.DictReader(open(sys.argv[1]))
for l in f:
    url = l['url'].replace('https://emptysqua.re/',
                           'http://localhost:1313/')

    if l['response'] == 'TRUE':
        response = requests.get(url)
        if response.status_code != 200:
            print(l['url'], response.status_code)
    elif l['response'] == 'FALSE':
        print('TODO: %s' % l['url'])
    elif l['response'].startswith('http'):
        # Expect a redirect.
        response = requests.get(url, allow_redirects=False)
        if response.status_code != 301:
            print(l['url'], response.status_code)
            print('\t expected redirect to %s' % l['response'])
        else:
            location = urljoin(url, response.headers['Location'])
            expected = l['response'].replace('https://emptysqua.re/',
                                             'http://localhost:1313/')

            if location != expected:
                print(l['url'], response.status_code, location)
                print('\t expected redirect to %s' % expected)
    else:
        print(url, 'UNKNOWN')


