#!/usr/bin/python3
import os, time, sys, yaml, json

import base64, random, string

from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
from urllib.request import urlopen
from collections import deque
import urllib3, io
import datetime
import markdownify

import argparse, re

parser = argparse.ArgumentParser(description='Process some stuff.')

parser.add_argument(
    '-D',
    '--outdir',
    type=str,
    dest='outdir',
    default="ctexts",
    help='Path to output directory')

args = parser.parse_args()

def getPage(url, headers):
    try:
        response = requests.get(url, headers=headers)
        text_content = response.text

        if str(response.status_code) == "200":
            #print("processed, http status: %s" % 200)
            pass
        else:
            print("http error: %s" % str(response.status_code))
            return ''
    except(urllib3.exceptions.LocationParseError, requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema) as err:    # add broken urls to it's own set, then continue
        print("skipping, http error: %s" % err)
        return ''
    return text_content

# https://celt.ucc.ie/publishd.html


# 1. get list page with BeautifulSoup
headers = ""
text_content = getPage('https://celt.ucc.ie/publishd.html', headers)
soup = BeautifulSoup(text_content, "lxml")
texts = set()
# 1. get links for html versions
for link in soup.find_all('a'):
    anchor = link.attrs["href"] if "href" in link.attrs else ''
    if 'published' in anchor:
        try: texts.add(anchor.split('/')[5])
        except IndexError:
            pass

try: os.mkdir(args.outdir)
except: pass

# 1. get full html page for each version
for text in texts:
    url = "%s/%s.%s" % ('https://celt.ucc.ie/published', text, "html")
    text_content = getPage(url, headers).replace("<DIV2>","DIV2")
    soup = BeautifulSoup(text_content, "lxml")
    # 1. get page title with BeautifulSoup
    try: title = soup.find_all('title')[0].text
    except IndexError: continue
    mdfile = re.sub('\W+','-', soup.find_all('title')[0].text.lower()) + ".md"
    try:
        markdown = markdownify.markdownify(text_content)
    except RecursionError:
        print(mdfile + "has error, skipping")
        continue
    markdown = re.sub('^' + title + '$', "#" + title, markdown, 1, flags=re.M)
    # 1. markdownify the html and store it as title.md writing frontmatter
    #print(markdownify.markdownify(text_content))
    file_handle = open("%s/%s" % (args.outdir, mdfile), 'w')
    file_handle.write(markdown)
    print(mdfile)    