from flask import Flask
from flask import request
from flask import json
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import url_for
from flask.ext.cors import CORS
from collections import Counter
import requests
import xmltodict
import re
#import xml

app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def index():
#  return render_template('index.html')
  return jsonify({
    'attribution': [
      'Free material from www.gapminder.org',
      'JSON API made by Ed Solis, edsfocci@gmail.com'],
    'instructions': [
      'Usage:',
      '\'GET /\':   Attribution and instructions of what URL paths and ' +
        'queries are available, along with a description of each.',

      '\'GET /datasets/\':   Metadata of each dataset, including ' +
        'spreadsheet *key*, *indicatorName*, *category* and *subcategory* ' +
        'the dataset belongs to, and the *dataprovider* and the ' +
        '*dataprovider_link*.',

      '\'GET /datasets/categories/\':   Shows a count of how many datasets ' +
        'belong to each category and subcategory.',

      '\'GET /datasets/categorized/\':   Shows which datasets belong to ' +
        'each category and subcategory.',

      '\'GET /data/help/?key=key\':   Shows which countries and years are ' +
        'available in the specified dataset.',

      '\'GET /data/?key=key&country=country&year=year\':   Gets the value ' +
        'for the specified country and year in the dataset.',

      '\'GET /data/?key=key&country=country\':   Gets the values for each ' +
        'available year in the dataset, for the specified country.',

      '\'GET /data/?key=key&year=year\':   Gets the values for each ' +
        'available country in the dataset, for the specified year.',

      '\'GET /data/?key=key\':   Downloads the CSV file of the whole ' +
        'dataset.']
  })

### DATASETS ###
@app.route('/datasets/')
def datasets():
  with open('private/datasets.json', 'r') as file:
    datasets = json.load(file)
  return jsonify(datasets)

@app.route('/datasets/categories/')
def datasets_categories():
  with open('private/datasets.json', 'r') as file:
    datasets = json.load(file)

  categories = {}
  for key in datasets:
    category = datasets[key]['category']
    subcategory = datasets[key]['subcategory']

    if not category in categories:
      categories[category] = Counter()

    categories[category][subcategory] += 1

  return jsonify(categories)

@app.route('/datasets/categorized/')
def datasets_categorized():
  with open('private/datasets.json', 'r') as file:
    datasets = json.load(file)

  categories = {}
  for key in datasets:
    category = datasets[key]['category']
    subcategory = datasets[key]['subcategory']
    indicator = datasets[key]['indicatorName']

    if not category in categories:
      categories[category] = {}

    if not subcategory in categories[category]:
      categories[category][subcategory] = []

    categories[category][subcategory].append(indicator)

  return jsonify(categories)

### DATA ###
@app.route('/data/')
def data():
  key = request.args.get('key')
  country = request.args.get('country')
  year = request.args.get('year')

  if not key:
    return "Spreadsheet key required."

  if year and country:
    col = get_col_specific_year(key, year)

    if type(col) == str:
      pass
    if col['status'] != 200:
      key = handle_redirect(key)
      col = get_col_specific_year(key, year)

    row = get_row_specific_country(key, country)

    if type(col) == str or type(row) == str:
      err = []
      if type(col) == str:
        err.append(col)
      if type(row) == str:
        err.append(row)
      return str(err)

    value = get_values_by('both', key, (row['data'], col['data']))
    value = {
      'status': col['status'],
      'data': {
        'country': country,
        'year': year,
        'value': value['content']['#text']
      }
    }

    return jsonify(value)

  elif year:
    col = get_col_specific_year(key, year)

    if type(col) == str:
      return col
    elif col['status'] != 200:
      key = handle_redirect(key)
      col = get_col_specific_year(key, year)

    countries = get_countries_available(key)
    countries['data'] = list(map(lambda i: {
      'country': i['content']['#text'],
      'row': re.search(r"R(\d+)C\d+$", i['id']).group(1)
    }, countries['data']))

    data = get_values_by('year', key, col['data'])

    def data_group(value):
      value_row = re.search(r"R(\d+)C\d+$", value['id']).group(1)
      country = list(filter(lambda j: j['row'] == value_row,
        countries['data']))[0]['country']

      return {
        'country': country,
        'year': year,
        'value': value['content']['#text']
      }

    data = { 'data': list(map(data_group, data)) }
    data['status'] = col['status']
    return jsonify(data)

  elif country:
    row = get_row_specific_country(key, country)

    if type(row) == str:
      return row
    elif row['status'] != 200:
      key = handle_redirect(key)
      row = get_row_specific_country(key, country)

    years = get_years_available(key)
    years['data'] = list(map(lambda i: {
      'year': i['content']['#text'],
      'col': re.search(r"R\d+C(\d+)$", i['id']).group(1)
    }, years['data']))

    data = get_values_by('country', key, row['data'])

    def data_group(value):
      value_col = re.search(r"R\d+C(\d+)$", value['id']).group(1)
      year = list(filter(lambda j: j['col'] == value_col,
        years['data']))[0]['year']

      return {
        'country': country,
        'year': year,
        'value': value['content']['#text']
      }

    data = { 'data': list(map(data_group, data)) }
    data['status'] = row['status']
    return jsonify(data)

  else:
    return redirect("http://spreadsheets.google.com/pub?key=" + key +
      "&output=csv", code=302)

@app.route('/data/help/')
def data_help():
  key = request.args.get('key')

  if not key:
    return "Spreadsheet key required."

  available = {}
  available['years'] = get_years_available(key)

  if available['years']['status'] != 200:
    key = handle_redirect(key)
    available['years'] = get_years_available(key)

  available['years']['data'] = list(map(lambda i: i['content']['#text'],
    available['years']['data']))

  available['countries'] = get_countries_available(key)
  available['countries']['data'] = list(map(lambda i: i['content']['#text'],
    available['countries']['data']))

  return jsonify(available)

### CLIENTS ###
@app.route('/clients/js/')
def clients_js():
  return render_template('js/index.html')

### HELPER FUNCTIONS ###
def get_years_available(key):
  years = requests.get('https://spreadsheets.google.com/feeds/cells/' +
    key + '/od6/public/basic',
    params={'min-row': 1, 'max-row': 1, 'min-col': 2})

  if years.status_code != 200:
    return { 'status': years.status_code }

  years_dict = { 'status': years.status_code }
  years_dict['data'] = xmltodict.parse(years.text)['feed']['entry']
  return years_dict

def get_countries_available(key):
  countries = requests.get('https://spreadsheets.google.com/feeds/cells/' +
    key + '/od6/public/basic',
    params={'min-col': 1, 'max-col': 1, 'min-row': 2})

  if countries.status_code != 200:
    return { 'status': countries.status_code }

  countries_dict = { 'status': countries.status_code }
  countries_dict['data'] = xmltodict.parse(countries.text)['feed']['entry']
  return countries_dict

def get_col_specific_year(key, year):
  avail_years = get_years_available(key)

  if avail_years['status'] != 200:
    return avail_years

  year = list(filter(lambda i: i['content']['#text'] == year,
    avail_years['data']))

  if len(year) == 0:
    return "Year not found."

  coords = { 'status': avail_years['status'] }
  coords['data'] = re.search(r"R\d+C(\d+)$", year[0]['id']).group(1)
  return coords

def get_row_specific_country(key, country):
  avail_countries = get_countries_available(key)

  if avail_countries['status'] != 200:
    return avail_countries

  country = list(filter(lambda i: i['content']['#text'] == country,
    avail_countries['data']))

  if len(country) == 0:
    return "Country not found."

  coords = { 'status': avail_countries['status'] }
  coords['data'] = re.search(r"R(\d+)C\d+$", country[0]['id']).group(1)
  return coords

def get_values_by(label_type, key, coord):
  if label_type == 'year':
    values = requests.get('https://spreadsheets.google.com/feeds/cells/' +
      key + '/od6/public/basic',
      params={'min-col': coord, 'max-col': coord, 'min-row': 2})
    return xmltodict.parse(values.text)['feed']['entry']

  elif label_type == 'country':
    values = requests.get('https://spreadsheets.google.com/feeds/cells/' +
      key + '/od6/public/basic',
      params={'min-row': coord, 'max-row': coord, 'min-col': 2})
    return xmltodict.parse(values.text)['feed']['entry']

  elif label_type == 'both':
    value = requests.get('https://spreadsheets.google.com/feeds/cells/' +
      key + '/od6/public/basic',
      params={'min-row': coord[0], 'max-row': coord[0],
        'min-col': coord[1], 'max-col': coord[1]})
    return xmltodict.parse(value.text)['feed']['entry']

  else:
    return ("Must specify whether to get values by 'year' or 'country', " +
    "or 'both'.")

def handle_redirect(key):
  redirect = requests.get('https://spreadsheets.google.com/pub',
    allow_redirects=False, params={'key': key})

  new_key = re.match(r"https:\/\/docs\.google\.com\/spreadsheets\/d\/" +
    r"(\S+)\/pub", redirect.headers['location']).group(1)
  return new_key

if __name__ == '__main__':
  app.run()

