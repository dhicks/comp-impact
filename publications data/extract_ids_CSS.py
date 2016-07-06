'''
Extract a list of IDs to retrieve from the CSS EndNote file
'''
import json
import xmltodict

## Infile: an xml file exported from EndNote
infile = 'database outputs/CSS pubs 2016-03-02.xml'
## Outfile: list of IDs
outfile = 'scraped pubs/ids_css.json'

with open(infile) as readfile:
	readdata = readfile.read()
readdata = xmltodict.parse(readdata)

records = readdata['xml']['records']['record']

dois = []
for record in records:
	try:
		doi = record['electronic-resource-num']['style']['#text']
	except KeyError:
		doi = ''
	dois += [doi]

with open(outfile, 'w') as writefile:
	json.dump(dois, writefile)

print('Extracted ' + str(len(dois)) + ' IDs to ' + outfile)
