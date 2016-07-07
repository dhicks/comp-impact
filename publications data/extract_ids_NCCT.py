'''
Extract a list of IDs to retrieve from the NCCT spreadsheet
'''
import json
import pandas as pd

## Infile: a CSV of NCCT publications
infile = 'database outputs/ToxCastTox21_sifter.csv'
## Outfile: list of IDs
outfile = 'scraped pubs/ids_ncct.csv'

readdata = pd.read_csv(infile, encoding = 'mac_roman')
readdata[['DOI', 'Pub Yr']].to_csv(outfile)

print('Extracted ' + str(len(readdata)) + ' IDs to ' + outfile)
