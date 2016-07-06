import html
import json
import pandas as pd
import re
import requests

from api_key import MY_API_KEY

def get_query (query):
	response = requests.get(query)
	note = []
	if response.status_code == 400:
		note += ['Scopus returned a parse error']
#	elif response.status_code == 401:
#		note = 'Scopus returned a parse error'
	elif response.status_code != 200:
		print('Query response ' + str(response.status_code))
		print(response.text)
		input()
	return {'title': title, 'response': response, 'note': note}
	
def parse_response (result):
	title = result['title']
	response = result['response']
	note = result['note']

	if response.status_code != 200 or 'service-error' in response:
		note += 'Query returned error: ' + str(response.status_code)
# 		print('exit 1')
		return {'title': title, 'doi': [], 'note': note}
	response = response.json()
	if 'search-results' not in response or \
		response['search-results']['opensearch:totalResults'] == '0' or \
		response['search-results']['opensearch:totalResults'] is None:
		note += ['No results']
# 		print('exit 2')
		return {'title': title, 'doi': [], 'note': note}
	
	n_results = int(response['search-results']['opensearch:totalResults'])
	if n_results > 1:
		note += ['Multiple results']

	hits = response['search-results']['entry']
	dois = []
	for hit in hits:
		if 'prism:doi' in hit:
			dois += [hit['prism:doi']]
	dois = list(set(dois))
	
	return {'title': title, 'doi': dois, 'note': note}
	
	

stics_data = pd.read_csv('database outputs/STICS output 2016-03-29.csv')
titles = stics_data['Title'].tolist()
## Many titles have HTML-escaped non-ascii characters, 
##  or other characters that will break the search string
titles = [html.unescape(title) for title in titles]
titles = [re.sub(r'[&#()?\r\n]', '', title) for title in titles]

data_q = []
data_uq = []

base_query = 'http://api.elsevier.com/content/search/scopus?'
for title in titles:
	print(title)
	query_q = base_query + 'query=title("' + title + '")&' + 'apiKey=' + MY_API_KEY
	query_uq = base_query + 'query=title(' + title + ')&' + 'apiKey=' + MY_API_KEY

	quoted = get_query(query_q)
	quoted = parse_response(quoted)
	data_q += [quoted]
	
	unquoted = get_query(query_uq)
	unquoted = parse_response(unquoted)
	data_uq += [unquoted]
	
data_q = pd.DataFrame(data_q)
data_q.to_csv('scraped pubs/stics_q.csv')
data_uq = pd.DataFrame(data_uq)
data_uq.to_csv('scraped pubs/stics_uq.csv')

