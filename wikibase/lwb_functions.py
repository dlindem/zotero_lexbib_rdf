import mwclient
import json
import urllib.parse
import time
import re
import requests
import sys
import unidecode

# LexBib wikibase OAuth
site = mwclient.Site('data.lexbib.org')
def get_token():
	global site
	with open('D:/LexBib/wikibase/data_lexbib_org_pwd.txt', 'r', encoding='utf-8') as pwdfile:
		pwd = pwdfile.read()

	login = site.login(username='DavidL', password=pwd)
	csrfquery = site.api('query', meta='tokens')
	token=csrfquery['query']['tokens']['csrftoken']
	print("Got fresh CSRF token for "+site+".")
	return token

knownqid = {}
# Loads known qid-lexbibUri mappings from jsonl-file
def load_knownqid():
	global knownqid
	try:
		with open('D:/LexBib/wikibase/knownqid.jsonl', encoding="utf-8") as f:
			mappings = f.read().split('\n')
			for mapping in mappings:
				if mapping != "":
					try:
						mappingjson = json.loads(mapping.replace("lexbibItem:","lexbibItem"))
						#print(mapping)
						knownqid[mappingjson['lexbibItem']] = mappingjson['qid']
					except Exception as ex:
						print('Found unparsable mapping json: '+mapping)
						print(str(ex))
						pass
			return knownqid

	except Exception as ex:
		print ('Error: knownqid file does not exist. Will start a new one.')
		print (str(ex))
		return knownqid
# Adds a new lexbibUri-qid mapping to knownqid.jsonl mapping file
def save_knownqid(mapping):
	with open('D:/LexBib/wikibase/knownqid.jsonl', 'a', encoding="utf-8") as jsonl_file:
		jsonl_file.write(json.dumps(mapping)+'\n')

# function for wikibase item creation (after check if it is known)
token = get_token()
def getqid(lwbclass, lexbibItem): # lwbclass: object of 'instance of' (P5), lexbibItem = lexbibUri (P3) of the (known or new) q-item
	global token
	global knownqid

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
					if 'Invalid CSRF token.' in str(ex):
						print('Wait a sec. Must get a new CSRF token...')
						token = get_token()
					else:
						print(str(ex))
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
					print('Instance-of-claim creation for '+lexbibItem+': success. Value = '+lwbclass)
					time.sleep(1)
					knownqid[lexbibItem] = qid
					save_knownqid({"lexbibItem":lexbibItem,"qid":qid})
					return qid
				else:
					print('Claim creation failed, will try again...')
					time.sleep(2)
		elif len(results) > 1:
			print('*** Error: Found more than one Wikibase item for one LexBib URI that should be unique... will take the first result.')
			qid = results[0]['lwbItem']['value'].replace("http://data.lexbib.org/entity/","")
			knownqid[lexbibItem] = qid
			save_knownqid({"lexbibItem":lexbibItem,"qid":qid})
			return qid
		elif len(results) == 1:
			qid = results[0]['lwbItem']['value'].replace("http://data.lexbib.org/entity/","")
			print('Found '+lexbibItem+' not in knownqid file but on data.lexbib: Qid '+qid+'; no need to create it, will add to knownqid file.')
			knownqid[lexbibItem] = qid
			save_knownqid({"lexbibItem":lexbibItem,"qid":qid})
			return qid
