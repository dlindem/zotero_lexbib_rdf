from tkinter import Tk
from tkinter.filedialog import askopenfilename
import mwclient
import traceback
import time
import sys
import os
import json
import re
#import requests
#import urllib.parse
import lwb

# open and load input file
print('Please select post-processed Zotero export JSON to be imported to data.lexbib.org.')
#time.sleep(2)
Tk().withdraw()
infile = askopenfilename()
infilename = os.path.basename(infile)
print('This file will be processed: '+infilename)
try:
	with open(infile, encoding="utf-8") as f:
		data =  json.load(f)
except Exception as ex:
	print ('Error: file does not exist.')
	print (str(ex))
	sys.exit()

totalrows = len(data)
#token = lwb.get_token()
#knownqid = lwb.load_knownqid()

with open('D:/LexBib/wikibase/logs/errorlog_'+infilename+'_'+time.strftime("%Y%m%d-%H%M%S")+'.log', 'w') as errorlog:
	index = 0
	edits = 0
	rep = 0

	while index < totalrows:
		if index >= 0: #start item in infile
			if rep > 4: # break 'while' loop after 5 failed attempts to process item
				print ('\nbibimport.py has entered in an endless loop... abort.')
				break
			else:
				print('\n'+str(index)+' items processed. '+str(totalrows-index)+' list items left.\n')
				#time.sleep(1)
				rep += 1

				try:
					item = data[index]
					qid = lwb.getqid("Q3", item['lexbibUri']) # Q3: LexBib BibItem class
					classStatement = lwb.updateclaim(qid,"P5",item['lexbibClass'],"item")
					for triple in item['creatorvals']:
						#check if creator with that position is already there as item (not literal)
						skip = False
						if triple['property'] == "P39":
							itemprop = "P12"
						elif triple['property'] == "P42":
							itemprop = "P13"
						for Qualifier in triple['Qualifiers']:
							if Qualifier['property'] == "P33":
								listpos = Qualifier['value']
								print('Found '+triple['property']+' creator listpos: ',listpos)
						creator_item_claims = lwb.getclaims(qid, itemprop)
						if itemprop in creator_item_claims:
							for creator_item_claim in creator_item_claims[itemprop]:
								creator_item_listpos = creator_item_claim['qualifiers']["P33"][0]['datavalue']['value']
								if creator_item_listpos == listpos:
									print('Found creator literal already replaced with creator item, will skip.')
									skip = True
						# if creator item claim for this creator listpos is not found, update literal
						if skip == False:
							statement = lwb.updateclaim(qid,triple['property'],triple['value'],triple['datatype'])
							if "Qualifiers" in triple:
								for qualitriple in triple['Qualifiers']:
									lwb.setqualifier(qid,triple['property'],statement, qualitriple['property'], qualitriple['value'], qualitriple['datatype'])

					for triple in item['propvals']:

						statement = lwb.updateclaim(qid,triple['property'],triple['value'],triple['datatype'])
						if "Qualifiers" in triple:
							for qualitriple in triple['Qualifiers']:
								lwb.setqualifier(qid,triple['property'],statement, qualitriple['property'], qualitriple['value'], qualitriple['datatype'])

				except Exception as ex:
					traceback.print_exc()
					lwb.logging.error('bibimport.py: Error at input line ['+str(index+1)+'] '+item['lexbibUri']+':'+str(ex))
					continue

				rep = 0
		index += 1

print('\nFinished. Check error log.')
