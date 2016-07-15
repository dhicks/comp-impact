import json
import os.path
import pandas as pd
import re
import requests
#import xmltodict

from api_key import ALTMETRICS_API_KEY

target_folder = 'publications data/'
## Infiles: A list of lists of IDs to work with, generated by an `extract_ids_` script
infiles = [target_folder + 'scraped pubs/combined dois.json']
## Outfiles
## List of Twitter accounts
tweeters_outfile = target_folder + 'twitter/tweeters.csv'
## List of all tweets
tweets_outfile = target_folder + 'twitter/tweets.csv'
## Paper metadata
metadata_outfile = target_folder + 'twitter/metadata.csv'

## Retrieve list of IDs
ids = []
for infile in infiles:
	with open(infile) as readfile:
		ids += json.load(readfile)
ids = set(ids[:])
print('Getting data for ' + str(len(ids)) + ' IDs from Altmetrics')
metadata = []
tweets = []

base_query_doi = 'http://api.altmetric.com/v1/fetch/doi/'
base_query_pmid = 'http://api.altmetric.com/v1/fetch/pmid/'

for id in ids:
	## Don't bother with empty IDs
	if id == '':
		continue
	## Altmetrics query
	## If the ID is 8 digits, it's a PubMed ID
	##  Otherwise it's a DOI
	if re.match(r'[0-9]{8}', id):
		query = base_query_pmid + id + '?key=' + ALTMETRICS_API_KEY
	else:
		query = base_query_doi + id + '?key=' + ALTMETRICS_API_KEY
	print('\t' + query)
	## Send the request
	response = requests.get(query)
	## Parse the status code
	status = response.status_code
	if status == 200:
		## Everything's fine
		pass
	elif status == 404:
		## Altmetrics didn't have any data for this ID
		print('\t\tNo data for ID ' + id)
		continue
	elif status == 420:
		print('Rate limited')
		exit(1)
	elif status == 502:
		print('API returned down for maintenance')
	
	## Convert the response into a dict
	response = json.loads(response.text)
	## Extract the paper metadata
	citation = response['citation']
	##  title
	try:
		title = citation['title']
	except KeyError:
		title = None
	##  DOI
	try:
		doi = citation['doi']
	except KeyError:
		doi = None
	##  PubMed ID
	try:
		pmid = citation['pmid']
	except KeyError:
		pmid = None
	##  journal
	try:
		journal = citation['journal']
	except KeyError:
		journal = None
	##  abstract
	try:
		abstract = citation['abstract']
		
	except KeyError:
		abstract = None
	##  first_seen_on
	try:
		first_seen = citation['first_seen_on']
	except KeyError:
		first_seen = None
	##  pubdate
	try:
		published = citation['pubdate']
	except KeyError:
		published = None
	try:
		n_tweets = len(response['posts']['twitter'])
	except (KeyError, TypeError):
		n_tweets = 0
	metadata += [{'doi': doi, 'pmid': pmid, 'title': title, 
					'abstract': abstract, 'journal': journal, 
					'first_seen': first_seen, 'published': published,
					'n_tweets': n_tweets}]
		
	## Extract the tweets
	try:
		these_tweets = response['posts']['twitter']
	except (KeyError, TypeError):
		these_tweets = []
# 	except TypeError:
# 		these_tweets = []
	## Record tweet metadata
	for tweet in these_tweets:
		account = '@' + tweet['author']['id_on_source']
		try:
			account_followers = tweet['author']['followers']
		except KeyError:
			account_followers = 0
		try:
			account_loc = tweet['author']['geo']['country']
		except KeyError:
			account_loc = ''
		try:
			account_desc = tweet['author']['description']
		except KeyError:
			account_desc = ''
		timestamp = tweet['posted_on']
		tweet_id = tweet['tweet_id']
		subject_paper = doi
		this_tweet = {'account': account, 
						'account_followers': account_followers,
						'account_loc': account_loc,
						'account_desc': account_desc,
						'timestamp': timestamp,
						'tweet_id': tweet_id, 
						'paper_doi': doi,
						'paper_pmid': pmid}
		tweets += [this_tweet]

## Arrange the results into data frames
## Paper metadata
metadata = pd.DataFrame(metadata)
## Tweets
tweets = pd.DataFrame(tweets)
## Tweeters
tweeters = tweets.groupby('account').agg({'tweet_id': 'count',
											'account_followers': 'max',
											'account_loc': 'first',
											'account_desc': 'first'}).\
			rename(columns = {'tweet_id': 'n_tweets',
								'account_followers': 'n_followers',
								'account_loc': 'location',
								'account_desc': 'description'})

## Save results in CSVs 
tweets.to_csv(tweets_outfile)
tweeters.to_csv(tweeters_outfile)
metadata.to_csv(metadata_outfile)
