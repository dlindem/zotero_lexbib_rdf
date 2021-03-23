import mwclient
import json
import urllib.parse
import time
import re
import csv
import requests
import sys
import unidecode
import logging
from wikidataintegrator import wdi_core, wdi_login
import config

# Properties with constraint: max. 1 value
max1props = ["P1","P2","P3","P4","P6","P8","P9","P10","P11","P14","P15","P16","P17","P22","P23","P24","P29","P30","P32","P34","P35","P36","P37","P38","P40","P41", "P46", "P65", "P87"]

# Logging config
logging.basicConfig(filename='logs/lwb.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')

# WDI setup

with open(config.datafolder+'wikibase/data_lexbib_org_bot_pwd.txt', 'r', encoding='utf-8') as pwdfile:
	lwbbotpass = pwdfile.read()
mediawiki_api_url = "https://data.lexbib.org/w/api.php" # <- change to applicable wikibase
sparql_endpoint_url = "https://data.lexbib.org/query/sparql"  # <- change to applicable wikibase
login = wdi_login.WDLogin(config.lwbuser, lwbbotpass, mediawiki_api_url=mediawiki_api_url)
lwbEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)

# LexBib wikibase OAuth for mwclient
with open(config.datafolder+'wikibase/data_lexbib_org_user_pwd.txt', 'r', encoding='utf-8') as pwdfile:
	lwbuserpass = pwdfile.read()
site = mwclient.Site('data.lexbib.org')
def get_token():
	global site
	global lwbpass

	login = site.login(username=config.lwbuser, password=lwbuserpass)
	csrfquery = site.api('query', meta='tokens')
	token=csrfquery['query']['tokens']['csrftoken']
	print("Got fresh CSRF token for data.lexbib.org.")
	return token
token = get_token()

# Loads known lwbqid-lexbibUri mappings and lwbqid-Wikidataqid mappins from jsonl-files
def load_knownqid():
	knownqid = {}
	try:
		with open(config.datafolder+'wikibase/mappings/lexbibmappings.csv', encoding="utf-8") as csvfile:
			rows = csv.reader(csvfile, delimiter=",")
			count = 0
			header = next(rows)
			for row in rows:
				count += 1
				if len(row) > 0:
					try:
						knownqid[row[0]] = row[1]
					except Exception as ex:
						print('Found unparsable mapping json in lexbibmappings.csv line ['+str(count)+']: ')
						print(str(ex))
						pass
	except Exception as ex:
		print ('Error: knownqid file does not exist. Will start a new one.')
		print (str(ex))
	#print(str(knownqid))
	print('Known LWB Qid loaded.')
	return knownqid
knownqid = load_knownqid()

def load_wdmappings():
	wdqids = {}
	try:
		with open(config.datafolder+'wikibase/mappings/wdmappings.jsonl', encoding="utf-8") as f:
			mappings = f.read().split('\n')
			count = 0
			for mapping in mappings:
				count += 1
				if mapping != "":
					try:
						mappingjson = json.loads(mapping)
						#print(mapping)
						wdqids[mappingjson['lwbqid']] = mappingjson['wdqid']
					except Exception as ex:
						print('Found unparsable mapping json in wdmappings.jsonl line ['+str(count)+']: '+mapping)
						print(str(ex))
						pass
	except Exception as ex:
		print ('Error: wdmappings file does not exist. Will start a new one.')
		print (str(ex))

	print('Known LWB-WD item mappings loaded.')
	return wdqids
wdqids = load_wdmappings()

# Adds a new lexbibUri-qid mapping to knownqid.jsonl mapping file
def save_knownqid(lexbibItem,qid):
	with open(config.datafolder+'wikibase/mappings/lexbibmappings.csv', 'a', encoding="utf-8") as csvfile:
		csvfile.write(lexbibItem+','+qid+'\n')

# Adds a new lwbqid-wdqid mapping to wdmappings.jsonl mapping file
def save_wdmapping(mapping):
	with open(config.datafolder+'wikibase/mappings/wdmappings.jsonl', 'a', encoding="utf-8") as jsonl_file:
		jsonl_file.write(json.dumps(mapping)+'\n')

# Get equivalent lwb item qidnum from wikidata Qid
def wdqid2lwbqid(wdqid):
	print('Will try to find lwbqid for '+wdqid+'...')
	global wdqids
	# Try to find lwbqid from known mappings
	for key, value in wdqids.items():
		if wdqid == value:
			print('Found lwbqid in wdqids known mappings.')
			return key
	# Try to find lwbqid via SPARQL
	url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0A%0Aselect%20%3FlwbItem%20where%0A%7B%20%3FlwbItem%20ldp%3AP4%20wd%3A"+wdqid+"%20.%20%7D"

	while True:
		try:
			r = requests.get(url)
			lwbqid = r.json()['results']['bindings'][0]['lwbItem']['value'].replace("http://data.lexbib.org/entity/","")
		except Exception as ex:
			print('Error: SPARQL request failed.')
			time.sleep(2)
			return False
		break
	print('Found lwbqid '+lwbqid+' not in mappingfile, but via SPARQL, will add it to mappingfile.')
	save_wdmapping({'lwbqid':lwbqid, 'wdqid':wdqid})
	return lwbqid

# creates a new item
def newitemwithlabel(lwbclasses, labellang, label): # lwbclass: object of 'instance of' (P5), lexbibItem = lexbibUri (P3) of the (known or new) q-item
	global token
	global knownqid
	if isinstance(lwbclasses, str) == True: # if a single value is passed as string, not as list
		lwbclasses = [lwbclasses]
	data = {"labels":{"en":{"language":labellang,"value":label}}}
	done = False
	while (not done):
		try:
			itemcreation = site.post('wbeditentity', token=token, new="item", bot=True, data=json.dumps(data))
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
			print('Item creation for '+qid+': success.')
		else:
			print('Item creation failed, will try again...')
			time.sleep(2)

		for lwbclass in lwbclasses:
			done = False
			while (not done):
				claim = {"entity-type":"item","numeric-id":int(lwbclass.replace("Q",""))}
				classclaim = site.post('wbcreateclaim', token=token, entity=qid, property="P5", snaktype="value", value=json.dumps(claim))
				try:
					if classclaim['success'] == 1:
						done = True
						print('Instance-of-claim creation for '+qid+': success. Class is '+lwbclass)
						#time.sleep(1)
				except:
					print('Claim creation failed, will try again...')
					time.sleep(2)
		return qid



# function for wikibase item creation (after check if it is known)
#token = get_token()
def getqid(lwbclasses, lexbibItem, onlyknown=False): # lwbclass: object of 'instance of' (P5), lexbibItem = lexbibUri (P3) of the (known or new) q-item
	global token
	global knownqid
	if isinstance(lwbclasses, str) == True: # if a single value is passed as string, not as list
		lwbclasses = [lwbclasses]
	if lexbibItem in knownqid:
		print(lexbibItem+' is a known wikibase item: Qid '+knownqid[lexbibItem]+', no need to create it.')
		return knownqid[lexbibItem]
	if onlyknown:
		return False
	lexbibItemSafe = urllib.parse.quote(lexbibItem, safe='~', encoding="utf-8")
	url = "https://data.lexbib.org/query/sparql?format=json&query=SELECT%20%3FlwbItem%20%0AWHERE%20%0A%7B%20%20%3FlwbItem%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2FP5%3E%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F"+lwbclasses[0]+"%3E.%20%0A%0A%20%20%20%3FlwbItem%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2FP3%3E%20%3C"+lexbibItemSafe+"%3E%20.%0A%7D"
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



		for lwbclass in lwbclasses:
			done = False
			while (not done):
				claim = {"entity-type":"item","numeric-id":int(lwbclass.replace("Q",""))}
				classclaim = site.post('wbcreateclaim', token=token, entity=qid, property="P5", snaktype="value", value=json.dumps(claim))
				try:
					if classclaim['success'] == 1:
						done = True
						print('Instance-of-claim creation for '+lexbibItem+': success. Class is '+lwbclass)
						#time.sleep(1)
				except:
					print('Claim creation failed, will try again...')
					time.sleep(2)
		knownqid[lexbibItem] = qid
		save_knownqid(lexbibItem,qid)
		return qid
	elif len(results) > 1:
		print('*** Error: Found more than one Wikibase item for one LexBib URI that should be unique... will take the first result.')
		qid = results[0]['lwbItem']['value'].replace("http://data.lexbib.org/entity/","")
		knownqid[lexbibItem] = qid
		save_knownqid(lexbibItem,qid)
		return qid
	elif len(results) == 1:
		qid = results[0]['lwbItem']['value'].replace("http://data.lexbib.org/entity/","")
		print('Found '+lexbibItem+' not in knownqid file but on data.lexbib: Qid '+qid+'; no need to create it, will add to knownqid file.')
		knownqid[lexbibItem] = qid
		save_knownqid(lexbibItem,qid)
		return qid

#get label
def getlabel(qid, lang):
	done = False
	while True:
		request = site.get('wbgetentities', ids=qid, props="labels", languages=lang)
		if request['success'] == 1:
			return request["entities"][qid]["labels"][lang]["value"]
		else:
			print('Something went wrong with label retrieval for '+qid+', will try again.')
			time.sleep(3)

#create item claim
def itemclaim(s, p, o):
	global token

	done = False
	value = json.dumps({"entity-type":"item","numeric-id":int(o.replace("Q",""))})
	while (not done):
		try:
			request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="value", value=value, bot=True)
			if request['success'] == 1:
				done = True
				claimId = request['claim']['id']
				print('Claim creation done: '+s+' ('+p+') '+o+'.')
				#time.sleep(1)
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print('Claim creation failed, will try again...\n'+str(ex))
				time.sleep(4)
	return claimId

#create string (or url) claim
def stringclaim(s, p, o):
	global token

	done = False
	value = '"'+o.replace('"', '\\"')+'"'
	while (not done):
		try:
			request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="value", value=value, bot=True)
			if request['success'] == 1:
				done = True
				claimId = request['claim']['id']
				print('Claim creation done: '+s+' ('+p+') '+o+'.')
				#time.sleep(1)
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print('Claim creation failed, will try again...\n'+str(ex))
				time.sleep(4)
	return claimId

#create string (or url) claim
def setlabel(s, lang, val, type="label"):
	global token

	done = False
	count = 0
	value = val # insert operations if necessary
	while count < 5:
		count += 1
		try:
			if type == "label":
				request = site.post('wbsetlabel', id=s, language=lang, value=value, token=token, bot=True)
			elif type == "alias":
				request = site.post('wbsetaliases', id=s, language=lang, add=value, token=token, bot=True)
			if request['success'] == 1:
				print('Label creation done: '+s+' ('+lang+') '+val+', type: '+type)
				return True
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			elif 'Unrecognized value for parameter "language"' in str(ex):
				print('Cannot set label in this language: '+lang)
				logging.warning('Cannot set label in this language: '+lang)
				break
			else:
				print('Label set operation '+s+' ('+lang+') '+val+' failed, will try again...\n'+str(ex))
				logging.error('Label set operation '+s+' ('+lang+') '+val+' failed, will try again...', exc_info=True)
				time.sleep(4)
	# log.add
	print ('*** Label set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	logging.warning('Label set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	return False

#create string (or url) claim
def setdescription(s, lang, val):
	global token

	done = False
	count = 0
	value = val # insert operations if necessary
	while count < 5:
		count += 1
		try:
			request = site.post('wbsetdescription', id=s, language=lang, value=value, token=token, bot=True)
			if request['success'] == 1:
				print('Description creation done: '+s+' ('+lang+') "'+val+'".')
				return True
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			elif 'Unrecognized value for parameter "language"' in str(ex):
				print('Cannot set description in this language: '+lang)
				logging.warning('Cannot set description in this language: '+lang)
				break
			elif 'already has label' in str(ex) and 'using the same description text.' in str(ex):
				# this is a hot candidate for merging
				print('*** Oh, it seems that we have a hot candidate for merging here... Writing info to mergecandidates.log')
				with open ('logs/mergecandidates.log', 'a', encoding='utf-8') as mergecandfile:
					mergecand = re.search(r'\[\[Item:(Q\d+)',str(ex)).group(1)
					mergecandfile.write(s+' and '+mergecand+' : '+val+'\n')
				break
			else:
				print('Description set operation '+s+' ('+lang+') '+val+' failed, will try again...\n'+str(ex))
				logging.error('Description set operation '+s+' ('+lang+') '+val+' failed, will try again...', exc_info=True)
				time.sleep(4)
	# log.add
	print ('*** Description set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	logging.warning('Description set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	return False

#get claims from qid
def getclaims(s, p):
	done = False
	while (not done):
		try:
			if p == True: # get all claims
				request = site.get('wbgetclaims', entity=s)
			else:
				request = site.get('wbgetclaims', entity=s, property=p)
			if "claims" in request:
				done = True
				return request['claims']
		except Exception as ex:
			print('Getclaims operation failed, will try again...\n'+str(ex))
			time.sleep(4)

#get claim from statement ID
def getclaimfromstatement(guid):
	done = False
	while (not done):
		try:
			request = site.get('wbgetclaims', claim=guid)

			if "claims" in request:
				done = True
				return request['claims']
		except Exception as ex:
			print('Getclaims operation failed, will try again...\n'+str(ex))
			time.sleep(4)

#update claims
def updateclaim(s, p, o, dtype): # for novalue: o="novalue", dtype="novalue"
	global max1props
	global token

	if dtype == "time":
		data=[(wdi_core.WDTime(o['time'], prop_nr=p, precision=o['precision']))]
		item = lwbEngine(wd_item_id=s, data=data)
		print('Successful time object write operation: '+item.write(login))
		# TBD: duplicate statement control
		claims = getclaims(s,p)
		#print(str(claims))
		return claims[p][0]['id']
	elif dtype == "string" or dtype == "url" or dtype == "monolingualtext":
		value = '"'+o.replace('"', '\\"')+'"'
	elif dtype == "item" or dtype =="wikibase-entityid":
		value = json.dumps({"entity-type":"item","numeric-id":int(o.replace("Q",""))})
	elif dtype == "novalue":
		value = "novalue"

	claims = getclaims(s,p)
	foundobjs = []
	if bool(claims):
		statementcount = 0
		for claim in claims[p]:
			statementcount += 1
			guid = claim['id']
			#print(str(claim['mainsnak']))
			if claim['mainsnak']['snaktype'] == "value":
				foundo = claim['mainsnak']['datavalue']['value']
			elif claim['mainsnak']['snaktype'] == "novalue":
				foundo = "novalue"
			if isinstance(foundo, dict): # foundo is a dict in case of datatype wikibaseItem
				#print(str(foundo))
				foundo = foundo['id']
			if foundo in foundobjs:
				print('Will delete a duplicate statement.')
				results = site.post('wbremoveclaims', claim=guid, token=token)
				if results['success'] == 1:
					print('Wb remove duplicate claim for '+s+' ('+p+') '+o+': success.')
			else:
				foundobjs.append(foundo)
				#print("A statement #"+str(statementcount)+" for prop "+p+" is already there: "+foundo)

				if foundo == o or foundo == value:
					print('Found redundant triple ('+p+') '+o+' >> Claim update skipped.')
					return guid

				elif p in max1props:
					print('It is a max 1 prop. Will replace statement.')

					while True:
						try:
							results = site.post('wbsetclaimvalue', token=token, claim=guid, snaktype="value", value=value)

							if results['success'] == 1:
								print('Claim update for '+s+' ('+p+') '+o+': success.')
								foundobjs.append(o)
								returnvalue = guid
								break
						except Exception as ex:
							if 'Invalid CSRF token.' in str(ex):
								print('Wait a sec. Must get a new CSRF token...')
								token = get_token()
							else:
								print('Claim update failed... Will try again.')
								time.sleep(4)

	if o not in foundobjs and value not in foundobjs: # must create new statement

		count = 0
		while count < 5:
			count += 1
			try:
				if dtype == "novalue":
					request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="novalue", bot=True)
				else:
					request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="value", value=value, bot=True)

				if request['success'] == 1:

					claimId = request['claim']['id']
					print('Claim creation done: '+s+' ('+p+') '+o+'.')
					return claimId

			except Exception as ex:
				if 'Invalid CSRF token.' in str(ex):
					print('Wait a sec. Must get a new CSRF token...')
					token = get_token()
				else:
					print('Claim creation failed, will try again...\n'+str(ex))
					logging.error('Claim creation '+s+' ('+p+') '+o+' failed, will try again...\n', exc_info=True)
					time.sleep(4)

		print ('*** Claim creation operation '+s+' ('+p+') '+o+' failed 5 times... skipped.')
		logging.warning('Label set operation '+s+' ('+p+') '+o+' failed 5 times... skipped.')
		return False
	else:
		return returnvalue



# set a Qualifier
def setqualifier(qid, prop, claimid, qualiprop, qualivalue, dtype):
	global token
	if dtype == "string" or dtype == "url" or dtype == "monolingualtext":
		qualivalue = '"'+qualivalue.replace('"', '\\"')+'"'
	elif dtype == "item" or dtype =="wikibase-entityid":
		qualivalue = json.dumps({"entity-type":"item","numeric-id":int(qualivalue.replace("Q",""))})

	# claims = getclaims(qid,prop)
	# foundobjs = []
	# if bool(claims):
	# 	statementcount = 0
	# 	for claim in claims[prop]:
	# 		if claim['id'] == claimid:
	#
	try:

		while True:
			setqualifier = site.post('wbsetqualifier', token=token, claim=claimid, property=qualiprop, snaktype="value", value=qualivalue, bot=True)
			# always set!!
			if setqualifier['success'] == 1:
				print('Qualifier set for '+qualiprop+': success.')
				return True
	except Exception as ex:
		if 'The statement has already a qualifier' in str(ex):
			print('**** The statement already has a qualifier (with the same hash)')
			return False


		print('Qualifier set failed, will try again...')
		logging.error('Qualifier set failed for '+prop+' ('+qualiprop+') '+qualivalue+': '+str(ex))
		time.sleep(2)

# set a Reference
def setref(claimid, refprop, refvalue, dtype):
	global token
	if dtype == "string" or dtype == "monolingualtext":
		refvalue = '"'+refvalue.replace('"', '\\"')+'"'
		valtype = "string"
	elif dtype == "url":
		# no transformation
		valtype = "string"
	elif dtype == "item" or dtype =="wikibase-entityid":
		refvalue = json.dumps({"entity-type":"item","numeric-id":int(refvalue.replace("Q",""))})
		valtype = "wikibase-entityid"
	snaks = json.dumps({refprop:[{"snaktype":"value","property":refprop,"datavalue":{"type":valtype,"value":refvalue}}]})
	while True:
		try:
			setref = site.post('wbsetreference', token=token, statement=claimid, index=0, snaks=snaks, bot=True)
			# always set at index 0!!
			if setref['success'] == 1:
				print('Reference set for '+refprop+': success.')
				return True
		except Exception as ex:
			#print(str(ex))
			if 'The statement has already a reference with hash' in str(ex):
				print('**** The statement already has a reference (with the same hash)')
				time.sleep(1)
			else:
				logging.error('Unforeseen exception: '+str(ex))
				print(str(ex))
				time.sleep(5)
			return False


		print('Reference set failed, will try again...')
		logging.error('Reference set failed for '+prop+' ('+refprop+') '+refvalue+': '+str(ex))
		time.sleep(2)

# Function for getting wikipedia url from wikidata qid (from https://stackoverflow.com/a/60811917)
def get_wikipedia_url_from_wikidata_id(wikidata_id, lang='en', debug=False):
	#import requests
	from requests import utils

	url = (
		'https://www.wikidata.org/w/api.php?action=wbgetentities&props=sitelinks/urls&ids='+wikidata_id+'&format=json')
	json_response = requests.get(url).json()
	if debug: print(wikidata_id, url, json_response)

	entities = json_response.get('entities')
	if entities:
		entity = entities.get(wikidata_id)
		if entity:
			sitelinks = entity.get('sitelinks')
			if sitelinks:
				if lang:
					# filter only the specified language
					sitelink = sitelinks.get(lang+'wiki')
					if sitelink:
						wiki_url = sitelink.get('url')
						if wiki_url:
							return requests.utils.unquote(wiki_url)
				else:
					# return all of the urls
					wiki_urls = {}
					for key, sitelink in sitelinks.items():
						wiki_url = sitelink.get('url')
						if wiki_url:
							wiki_urls[key] = requests.utils.unquote(wiki_url)
					return wiki_urls
	return None

#remove claim
def removeclaim(guid):
	global token
	done = False
	while (not done):
		try:
			results = site.post('wbremoveclaims', claim=guid, token=token)
			if results['success'] == 1:
				print('Wb remove claim for '+guid+': success.')
				done = True
		except Exception as ex:
			print('Removeclaim operation failed, will try again...\n'+str(ex))
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			if 'invalid-guid' in str(ex):
				print('The guid to remove was not found.')
				done = True
			time.sleep(4)
