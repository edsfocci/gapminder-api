import requests
import xmltodict
#import xml

def data():
  key = 'phAwcNAVuyj0TAlJeCEzcGQ'
  r = requests.get('https://spreadsheets.google.com/feeds/worksheets/' + key +
    '/public/basic')
  x = xmltodict.parse(r.text)['feed']
  # x.keys(): ['@xmlns', '@xmlns:openSearch', '@xmlns:gs', 'id', 'updated',
  #  'category', 'title', 'link', 'author', 'openSearch:totalResults',
  #  'openSearch:startIndex', 'entry']

#  for key in x:
#    print key
#    print x[key]
  print len(x['entry'])

#  print x['updated']
#  print x['entry'][0]['content']['#text']
#  print x['entry'][0]['link']

#  r = requests.get('https://spreadsheets.google.com/feeds/cells/' + key +
#    '/od6/public/basic',
#    params={'min-row': '1', 'max-row': '1'})
#  print r.text

data()
