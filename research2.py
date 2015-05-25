from flask import json
import requests
import re
#import xmltodict

def data():
#  with open('private/datasets.json', 'r') as file:
#    datasets = json.load(file)

#  for key in datasets:
#    print key

  key = 'rjhBvpeRgCxBq0EnQVN6b0w'
  r = requests.get('https://spreadsheets.google.com/feeds/cells/' +
    key + '/od6/public/basic',
    params={'min-row': 1, 'max-row': 1, 'min-col': 2})
  if r.status_code != 200:
    r = requests.get('https://spreadsheets.google.com/pub',
      allow_redirects=False,
      params={'key': key})
    new_key = re.match(r"https:\/\/docs\.google\.com\/spreadsheets\/d\/" +
      r"(\S+)\/pub", r.headers['location']).group(1)
    print new_key

data()
