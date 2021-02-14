from tkinter import Tk
from tkinter.filedialog import askopenfilename
import mwclient
import traceback
import time
import sys
import os
import json
import re
import requests
import urllib.parse

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

# Load known qid-lexbibUri mappings
knownqid = {}
try:
	with open('D:/LexBib/wikibase/knownqid.jsonl', encoding="utf-8") as f:
		mappings = f.readlines()
		for mapping in mappings:
			try:
				mapping = mapping.json()
				knownqid[mapping['lexbibItem']] = mapping['qid']
			except:
				pass

except Exception as ex:
	print ('Error: knownqid file does not exist. Will start a new one.')
	print (str(ex))

def save_knownqid(mapping):
	with open('D:/LexBib/wikibase/knownqid.jsonl', 'a', encoding="utf-8") as jsonl_file:
		jsonl_file.write(json.dumps(mapping)+'\n')

# function for item creation (after check if it is known)
def getqid(lwbclass, lexbibItem, token):

	if lexbibItem in knownqid:
		print(lexbibItem+' is a known wikibase item: Qid '+knownqid[lexbibItem]+', no need to create it.')
		return knownqid[lexbibItem]
	else:
		lexbibItemSafe = urllib.parse.quote(lexbibItem, safe='~', encoding="utf-8", errors="strict")
		url = "https://data.lexbib.org/query/sparql?format=json&query=SELECT%20%3FlwbItem%20%0AWHERE%20%0A%7B%20%20%3FlwbItem%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2FP5%3E%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F"+lwbclass+"%3E.%20%0A%0A%20%20%20%3FlwbItem%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2FP3%3E%20%3C"+lexbibItemSafe+"%3E%20.%0A%7D"
		done = False
		while (not done):
			try:
				r = requests.get(url)
				results = r.json()['results']['bindings']
			except Exception as ex:
				print('Error: SPARQL request failed.')
				time.sleep(2)
				continue
			done = True
		if len(results) == 0:
			print('Found no Qid for LexBib URI '+lexbibItem+', will create it.')
			claim = {"claims":[{"mainsnak":{"snaktype":"value","property":"P3","datavalue":{"value":lexbibItem,"type":"string"}},"type":"statement","rank":"normal"}]}
			done = False
			while (not done):
				try:
					itemcreation = site.post('wbeditentity', token=token, new="item", bot=True, data=json.dumps(claim))
				except Exception as ex:
					print(str(ex))
					if 'Invalid CSRF token.' in str(ex) or 'referenced before assignment' in str(ex):
						print('Wait a sec. Must get a new CSRF token...')
						token = get_token()
					else:
						time.sleep(4)
					continue
				#print(str(itemcreation))
				if itemcreation['success'] == 1:
					done = True
					qid = itemcreation['entity']['id']
					print('Item creation for '+lexbibItem+': success. QID = '+qid)
				else:
					print('Item creation failed, will try again...')
					time.sleep(2)
			done = False
			while (not done):
				claim = {"entity-type":"item","numeric-id":int(lwbclass.replace("Q",""))}
				classclaim = site.post('wbcreateclaim', token=token, entity=qid, property="P5", snaktype="value", value=json.dumps(claim))
				if classclaim['success'] == 1:
					done = True
					print('Claim creation for '+lexbibItem+': success. Class = '+lwbclass)
					knownqid[lexbibItem] = qid
					save_knownqid({"lexbibItem:":lexbibItem,"qid":qid})
					return qid
				else:
					print('Claim creation failed, will try again...')
					time.sleep(2)
		elif len(results) > 1:
			print('*** Error: Found more than one Wikibase item for one LexBib URI that should be unique... will take the first result.')
			qid = results[0]['lwbItem']['value'].replace("http://data.lexbib.org/entity/","")
			knownqid[lexbibItem] = qid
			save_knownqid({"lexbibItem:":lexbibItem,"qid":qid})
			return qid
		elif len(results) == 1:
			qid = results[0]['lwbItem']['value'].replace("http://data.lexbib.org/entity/","")
			print('Found '+lexbibItem+' not in knownqid file but on data.lexbib: Qid '+qid+'; no need to create it, will add to knownqid file.')
			knownqid[lexbibItem] = qid
			save_knownqid({"lexbibItem:":lexbibItem,"qid":qid})
			return qid



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
				qid = getqid("Q3", item['lexbibUri'], token)
				for prop in item['propvals']:

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
				errorlog.write('\n\nError at input line ['+str(index+1)+'] '+item['lexbibUri']+'\n'+str(ex))
				continue
			index += 1
			rep = 0
		else:
			print ('\n...this script has entered in an endless loop... Abort.')
			break
