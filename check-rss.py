#!/usr/bin/env python
import argparse
import sys
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup


def check_img_tags(feed_url):
    accessible = []
    inaccessible = []
    response = requests.get(feed_url)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    for item in root.findall('.//item'):
        description = item.find('description')
        if description is not None:
            soup = BeautifulSoup(description.text, 'html.parser')
            for img_tag in soup.find_all('img'):
                img_url = img_tag.get('src')
                if img_url:
                    try:
                        requests.head(img_url, allow_redirects=True).raise_for_status()
                        accessible.append(img_url)
                    except Exception as e:
                        print(img_url)
                        print(e)
                        inaccessible.append(img_url)

    print("Successful:")
    for url in accessible:
        print(url)

    return 1 if len(inaccessible) > 0 else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("feed_url", help="URL of RSS feed")
    sys.exit(check_img_tags(parser.parse_args().feed_url))
