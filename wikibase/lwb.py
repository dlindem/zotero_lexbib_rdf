import mwclient
import json
import urllib.parse
import time
import re
import requests
import sys
import unidecode

# Properties with constraint: max. 1 value
max1props = ["P1","P2","P3","P4","P6","P8","P9","P10","P11","P14","P15","P16","P17","P22","P23","P24","P29","P30","P32","P34","P35","P36","P37","P38","P40","P41"]

# LexBib wikibase OAuth
site = mwclient.Site('data.lexbib.org')
def get_token():
	global site
	with open('D:/LexBib/wikibase/data_lexbib_org_pwd.txt', 'r', encoding='utf-8') as pwdfile:
		pwd = pwdfile.read()

	login = site.login(username='DavidL', password=pwd)
	csrfquery = site.api('query', meta='tokens')
	token=csrfquery['query']['tokens']['csrftoken']
	print("Got fresh CSRF token for data.lexbib.org.")
	return token
token = get_token()

# Loads known qid-lexbibUri mappings from jsonl-file
def load_knownqid():
	knownqid = {}
	try:
		with open('D:/LexBib/wikibase/knownqid.jsonl', encoding="utf-8") as f:
			mappings = f.read().split('\n')
			count = 0
			for mapping in mappings:
				count += 1
				if mapping != "":
					try:
						mappingjson = json.loads(mapping.replace("lexbibItem:","lexbibItem"))
						#print(mapping)
						knownqid[mappingjson['lexbibItem']] = mappingjson['qid']
					except Exception as ex:
						print('Found unparsable mapping json in knownqid.jsonl line ['+str(count)+']: '+mapping)
						print(str(ex))
						pass
	except Exception as ex:
		print ('Error: knownqid file does not exist. Will start a new one.')
		print (str(ex))

	print('Known LWB Qid loaded.')
	return knownqid
knownqid = load_knownqid()

# Adds a new lexbibUri-qid mapping to knownqid.jsonl mapping file
def save_knownqid(mapping):
	with open('D:/LexBib/wikibase/knownqid.jsonl', 'a', encoding="utf-8") as jsonl_file:
		jsonl_file.write(json.dumps(mapping)+'\n')

# function for wikibase item creation (after check if it is known)
#token = get_token()
def getqid(lwbclasses, lexbibItem): # lwbclass: object of 'instance of' (P5), lexbibItem = lexbibUri (P3) of the (known or new) q-item
	global token
	global knownqid
	if isinstance(lwbclasses, str) == True: # if a single value is passed as string, not as list
		lwbclasses = [lwbclasses]

	if lexbibItem in knownqid:
		print(lexbibItem+' is a known wikibase item: Qid '+knownqid[lexbibItem]+', no need to create it.')
		return knownqid[lexbibItem]
	else:
		lexbibItemSafe = urllib.parse.quote(lexbibItem, safe='~', encoding="utf-8", errors="strict")
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
			save_knownqid({"lexbibItem":lexbibItem,"qid":qid})
			return qid
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
def setlabel(s, lang, val):
	global token

	done = False
	value = val # insert operations if necessary
	while (not done):
		try:
			request = site.post('wbsetlabel', id=s, language=lang, value=value, token=token, bot=True)
			if request['success'] == 1:
				done = True
				print('Label creation done: '+s+' ('+lang+') '+val+'.')
				#time.sleep(1)
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print('Label set operation failed, will try again...\n'+str(ex))
				time.sleep(4)
	return True

#get claims
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

#update claims
def updateclaim(s, p, o, dv):
	global max1props
	global token

	if dv == "string" or dv == "url":
		value = '"'+o.replace('"', '\\"')+'"'
	elif dv == "item":
		value = json.dumps({"entity-type":"item","numeric-id":int(o.replace("Q",""))})

	claims = getclaims(s,p)
	foundobjs = []
	if bool(claims):
		statecount = 0
		for claim in claims[p]:
			statecount += 1
			guid = claim['id']
			foundo = claim['mainsnak']['datavalue']['value']
			if foundo in foundobjs:
				print('Will delete a duplicate statement.')
				results = site.post('wbremoveclaims', claim=guid, token=token)
				if results['success'] == 1:
					print('Wb remove duplicate claim for '+s+' ('+p+') '+o+': success.')
			else:
				foundobjs.append(foundo)
				print("A statement #"+str(statecount)+" is already there: "+foundo)

				if foundo == o or foundo == value:
					print('Found redundant object. Claim update skipped.')
					returnvalue = guid

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

		while True:
			try:
				request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="value", value=value, bot=True)

				if request['success'] == 1:

					claimId = request['claim']['id']
					print('Claim creation done: '+s+' ('+p+') '+o+'.')
					returnvalue = claimId
					break
					#time.sleep(1)
			except Exception as ex:
				if 'Invalid CSRF token.' in str(ex):
					print('Wait a sec. Must get a new CSRF token...')
					token = get_token()
				else:
					print('Claim creation failed, will try again...\n'+str(ex))
					time.sleep(4)

	return returnvalue
