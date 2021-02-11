import requests
import urllib.parse
import time
import mwclient
import json

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
try:
	with open('D:/LexBib/wikibase/knownqid.json', encoding="utf-8") as f:
		knownqid =  json.load(f)
except Exception as ex:
	print ('Error: knownqid file does not exist. Will start a new one.')
	print (str(ex))
	knownqid = {}

def save_knownqid(qid):
	with open('D:/LexBib/wikibase/knownqid.json', 'w', encoding="utf-8") as json_file:
		json.dump(knownqid, json_file, indent=2)


def getqid(lwbclass, lexbibItem):

	if lexbibItem in knownqid:
		print('This is a known bibitem: Qid '+knownqid[lexbibItem])
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
			print('*** Found no Qid for LexBib URI '+lexbibItem+', will create it.')
			claim = {"claims":[
			#{"mainsnak":{"snaktype":"value","property":"P5","datavalue":{"value":lwbclass,"type":"WikibaseItem"}},"type":"statement","rank":"normal"},
			{"mainsnak":{"snaktype":"value","property":"P3","datavalue":{"value":lexbibItem,"type":"string"}},"type":"statement","rank":"normal"}
			]}
			token = get_token()
			done = False
			while (not done):
				itemcreation = site.post('wbeditentity', token=token, new="item", bot=True, data=json.dumps(claim))
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
					save_knownqid(qid)
					return qid
				else:
					print('Claim creation failed, will try again...')
					time.sleep(2)
		elif len(results) > 1:
			print('*** Error: Found more than one Wikibase item for one LexBib URI that should be unique... will take the first result.')
			qid = results[0]['lwbItem']['value'].replace("http://data.lexbib.org/entity/","")
			knownqid[lexbibItem] = qid
			save_knownqid(qid)
			return qid
		elif len(results) == 1:
			qid = results[0]['lwbItem']['value'].replace("http://data.lexbib.org/entity/","")
			knownqid[lexbibItem] = qid
			save_knownqid(qid)
			return qid
