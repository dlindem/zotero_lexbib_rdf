from SPARQLWrapper import SPARQLWrapper, JSON
import time
import sys
import json
import requests
import mwclient
import lwb # functions for data.lexbib.org (LWB: LexBib WikiBase) I/O operations

# class of items to be enriched from Wikidata, example "Q8" for language
c = "Q9"
print ('LWB class to be updated is: '+c)

# List of LWB properties to be taken values for from Wikidata
# For properties, e.g. "P65"; for wikipedia English sitelink, "en.wiki"; "en.label" for English label.
# This should come from a property schema for the selected LWB class (TBD)
props = [
"en.label"
]

# Get LWB items belonging to class c
url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX lwb%3A <http%3A%2F%2Fdata.lexbib.org%2Fentity%2F>%0APREFIX ldp%3A <http%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F>%0A%0ASELECT %3Fitem %3Fwdqid WHERE {%0A%3Fitem ldp%3AP5 lwb%3A"+c+" .%0A%3Fitem ldp%3AP4 %3Fwdqid .}%0A"
done = False
while (not done):
	try:
		r = requests.get(url)
		lwbitems = r.json()['results']['bindings']
	except Exception as ex:
		print('Error: SPARQL request failed: '+str(ex))
		time.sleep(2)
		continue
	done = True
#print(str(lwbitems))

wikidata = mwclient.Site('wikidata.org')

for prop in props:
	if prop == "en.wiki":
		# get en.wikipedia url and write it to LWB using P66
		itemcount = 1
		for item in lwbitems:
			print('\nItem ['+str(itemcount)+'], '+str(len(lwbitems)-itemcount)+' items left.')
			wdqid = item['wdqid']['value'].replace("http://www.wikidata.org/entity/","")
			lwbqid = item['item']['value'].replace("http://data.lexbib.org/entity/","")
			print('Will now get en.wikipedia page url for LWB item: '+lwbqid+' from wdItem: '+wdqid)
			enwikiurl = lwb.get_wikipedia_url_from_wikidata_id(wdqid, lang='en', debug=True)
			lwb.stringclaim (lwbqid,"P66",enwikiurl)
			itemcount += 1
	elif prop == "en.label":
		# get label (English), and write it to LWB
		itemcount = 1
		for item in lwbitems:
			print('\nItem ['+str(itemcount)+'], '+str(len(lwbitems)-itemcount)+' items left.')
			wdqid = item['wdqid']['value'].replace("http://www.wikidata.org/entity/","")
			lwbqid = item['item']['value'].replace("http://data.lexbib.org/entity/","")
			print('Will now get label (English) for LWB item: '+lwbqid+' from wdItem: '+wdqid)
			done = False
			while (not done):
				try:
					r = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=labels&ids="+wdqid+"&languages=en").json()
					#print(str(r))
					if "labels" in r['entities'][wdqid]:
						label = r['entities'][wdqid]['labels']['en']['value']
						done = True

				except Exception as ex:
					print('Wikidata: Getlabels operation failed, will try again...\n'+str(ex))
					time.sleep(4)

			lwb.setlabel (lwbqid,"en",label)
			itemcount += 1
	else:
		# get wikidata equivalent prop
		wdprop = lwb.getclaims(prop, "P2")
		if bool(wdprop):
			wdprop = wdprop['P2'][0]['mainsnak']['datavalue']['value'].replace("http://www.wikidata.org/entity/","")
			print('Wikidata Prop for LWB prop '+prop+' is: '+wdprop)
		else:
			print('*** No equivalent Wikidata property found for '+prop+'.')
			continue
		itemcount = 1
		for item in lwbitems:
			print('\nItem ['+str(itemcount)+'], '+str(len(lwbitems)-itemcount)+' items left.')
			wdqid = item['wdqid']['value'].replace("http://www.wikidata.org/entity/","")
			lwbqid = item['item']['value'].replace("http://data.lexbib.org/entity/","")
			print('Will now update LWB item: '+lwbqid+' from wdItem: '+wdqid)
			done = False
			while (not done):
				try:
					request = wikidata.get('wbgetclaims', entity=wdqid, property=wdprop)
				except Exception as ex:
					print('Wikidata: Getclaims operation failed, will try again...\n'+str(ex))
					time.sleep(4)
				if "claims" in request:
					done = True
					itemcount += 1
			if bool(request['claims']): # i.e. if claims is not empty and contains a list (of claims)
				for claim in request['claims'][wdprop]:
					if claim['mainsnak']['snaktype'] == "value":
						dtype = claim['mainsnak']['datavalue']['type']

						if dtype == "wikibase-entityid":
							wdqid = claim['mainsnak']['datavalue']['value']['id']
							value = lwb.wdqid2lwbqid(wdqid)
							#value = json.dumps({"entity-type":"item","numeric-id":lwbqidnum})
							if value == False:
								print('No LWB item found for Wikidata '+wdqid+'. Skipped...')
								lwb.logging.warning('classwdupdate: No LWB item (should be one of class '+c+' found for Wikidata '+wdqid+'.')
								continue
						elif dtype == "string":
							value = claim['mainsnak']['datavalue']['value']

						statement = lwb.updateclaim(lwbqid,prop,value,dtype)
						reference = lwb.setref(statement,"P4",item['wdqid']['value'],"url")
			else:
				print('No claim on Wikidata.')
				itemcount += 1





# lwbsparql = SPARQLWrapper("https://data.lexbib.org/query/sparql", agent='LexBib (lexbib.org)')
# lwbsparql.setQuery("""PREFIX ldp: <http://data.lexbib.org/prop/direct/>
# 					SELECT ?item ?class WHERE {
# 						?item ldp:P5 ?class .
# 					}""")
# lwbsparql.setReturnFormat(JSON)
# while True:
# 	try:
# 		time.sleep(1.5)
# 		result = lwbsparql.query().convert()
# 		datalist = result['results']['bindings']
# 		print(str(result))
# 		break
# 	except Exception as ex:
# 		print(str(ex))
# 		time.sleep(4)

# site = mwclient.Site('data.lexbib.org')
#
#
#
# wdsparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='LexBib-Wikidata-Recon-Script (data.lexbib.org)')
# #query wikidata for
#
# sparql.setQuery("""SELECT ?label ?country ?countrylabel
# 					WHERE {
# 						wd:"""+wdid+""" rdfs:label ?label .
# 						FILTER (langMatches( lang(?label), "EN" ) )
# 						wd:"""+wdid+""" wdt:P17 ?country.
# 						?country rdfs:label ?countrylabel .
# 						FILTER (langMatches( lang(?countrylabel), "EN" ) )
# 						} limit 1""")
# 		sparql.setReturnFormat(JSON)
# 		wdquerycount = wdquerycount + 1
# 		try:
# 			time.sleep(1.5)
# 			wddict = sparql.query().convert()
# 			datalist = wddict['results']['bindings']
# 			print(datalist[0])
