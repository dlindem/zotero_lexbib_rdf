from tkinter import Tk
from tkinter.filedialog import askopenfilename
import mwclient
import traceback
import time
import sys
import os
import json
import re
import getqid

# LexBib wikibase OAuth
site = mwclient.Site('data.lexbib.org')
with open('D:/LexBib/wikibase/data_lexbib_org_pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()
def get_token():
	login = site.login(username='DavidL', password=pwd)
	csrfquery = site.api('query', meta='tokens')
	token=csrfquery['query']['tokens']['csrftoken']
	print("Got fresh CSRF token.")
	return token

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
token = get_token()

with open('D:/LexBib/wikibase/logs/errorlog_'+infilename+'_'+time.strftime("%Y%m%d-%H%M%S")+'.log', 'w') as errorlog:
	index = 0
	edits = 0
	rep = 0

	while index < totalrows:
		if rep < 6: # break while loop after 5 time trying to resolve the same job
			print('\nList item Nr. '+str(index)+' processed. '+str(totalrows-index)+' list items left.\n')
			#time.sleep(1)
			rep += 1

			try:
				item = data[index]
				qid = getqid.getqid("Q3", item['lexbibUri'])
				for proplist in item['props']:
					for prop in proplist:
						#print(prop)
						if "string" in prop:
							value = '"'+prop['string'].replace('"', '\\"').replace("'", '\\"')+'"'
							#print (value)
							done = False
							while (not done):
								createclaim = site.post('wbcreateclaim', token=token, entity=qid, property=prop['property'], snaktype="value", value=value, bot=True)
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
								results = site.post('wbcreateclaim', token=token, entity=qid, property=prop['property'], snaktype="value", bot=True, value=json.dumps(value))
								if createclaim['success'] == 1:
									done = True
									print('Claim creation for'+prop['property']+': success.')
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
									setqualifier = site.post('wbsetqualifier', token=token, claim=claimid, property=qualiprop, snaktype="value", value=qualivalue, bot=True)
									if setqualifier['success'] == 1:
										done = True
										print('Qualifier set for '+qualiprop+': success.')
									else:
										print('Qualifier set failed, will try again...')
										time.sleep(2)

			except Exception as ex:
				traceback.print_exc()
				if 'Invalid CSRF token.' in str(ex):
					print('Wait a sec. Must get a new CSRF token...')
					token = get_token()
				errorlog.write('\n\nError at input line ['+str(index+1)+'] "'+item['lexbibUri']+'" ('+qid+'): \n'+str(ex))
				continue
			index += 1
			rep = 0
		else:
			print ('\n...this script has entered in an endless loop... Abort.')
			break
