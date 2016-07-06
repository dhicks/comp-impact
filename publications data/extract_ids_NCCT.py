'''
Extract a list of IDs to retrieve from the NCCT spreadsheet
'''
import json
import pandas as pd

## Infile: a CSV of NCCT publications
infile = 'database outputs/ToxCastTox21_sifter.csv'
## Outfile: list of IDs
outfile = 'scraped pubs/ids_ncct.json'

readdata = pd.read_csv(infile, encoding = 'mac_roman')

ids = readdata['DOI'].astype(str).drop_duplicates().tolist()

with open(outfile, 'w') as writefile:
	json.dump(ids, writefile)

print('Extracted ' + str(len(ids)) + ' IDs to ' + outfile)
