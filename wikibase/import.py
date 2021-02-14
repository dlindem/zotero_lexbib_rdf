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
import lwb_functions

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
#token = lwb_functions.get_token()
knownqid = lwb_functions.load_knownqid()

with open('D:/LexBib/wikibase/logs/errorlog_'+infilename+'_'+time.strftime("%Y%m%d-%H%M%S")+'.log', 'w') as errorlog:
	index = 0
	edits = 0
	rep = 0

	while index < totalrows:
		if rep > 4: # break while loop after 4 fails to process item
			print ('\n...this script has entered in an endless loop... Abort.')
			break
		else:
			print('\nList item Nr. '+str(index)+' processed. '+str(totalrows-index)+' list items left.\n')
			#time.sleep(1)
			rep += 1

			try:
				item = data[index]
				qid = lwb_functions.getqid("Q3", item['lexbibUri'])
				for prop in item['propvals']:

					#print(prop)
					if "string" in prop:
						value = '"'+prop['string'].replace('"', '\\"')+'"'
						#print (value)
						done = False
						while (not done):
							createclaim = lwb_functions.site.post('wbcreateclaim', token=lwb_functions.token, entity=qid, property=prop['property'], snaktype="value", value=value, bot=True)
							if createclaim['success'] == 1:
								done = True
								print('Claim creation for '+prop['property']+': success.')
								claimid = createclaim['claim']['id']
							else:
								print('Claim creation failed, will try again...')
								time.sleep(2)
					if "qid" in prop:
						done = False
						value = {"entity-type":"item","numeric-id":int(prop['qid'].replace("Q",""))}
						while (not done):
							results = lwb_functions.site.post('wbcreateclaim', token=lwb_functions.token, entity=qid, property=prop['property'], snaktype="value", bot=True, value=json.dumps(value))
							if createclaim['success'] == 1:
								done = True
								print('Claim creation for '+prop['property']+': success.')
								claimid = createclaim['claim']['id']
							else:
								print('Claim creation failed, will try again...')
								time.sleep(2)
					if "Qualifiers" in prop:
						for qualiprop in prop['Qualifiers']:
							qualivalue = '"'+prop['Qualifiers'][qualiprop].replace('"', '\\"').replace("'", '\\"')+'"'
							#print(qualivalue)
							done = False
							while (not done):
								setqualifier = lwb_functions.site.post('wbsetqualifier', token=lwb_functions.token, claim=claimid, property=qualiprop, snaktype="value", value=qualivalue, bot=True)
								if setqualifier['success'] == 1:
									done = True
									print('Qualifier set for '+qualiprop+': success.')
								else:
									print('Qualifier set failed, will try again...')
									time.sleep(2)

			except Exception as ex:
				if 'Invalid CSRF token.' in str(ex):
					print('Wait a sec. Must get a new CSRF token...')
					lwb_functions.token = lwb_functions.get_token()
				else:
					traceback.print_exc()
					errorlog.write('\n\nError at input line ['+str(index+1)+'] '+item['lexbibUri']+'\n'+str(ex))
				continue
			index += 1
			rep = 0
