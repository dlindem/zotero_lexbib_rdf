from SPARQLWrapper import SPARQLWrapper, JSON
import time
import sys
import json
import requests
import mwclient
import lwb

# class of items to be enriched from Wikidata, example "Q8" for language
c = "Q8"
print ('LWB class to be updated is: '+c)

# List of LWB properties to be taken values for from Wikidata
props = [
"P43"
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
print(str(lwbitems))

wikidata = mwclient.Site('wikidata.org')
for prop in props:
	# get wikidata equivalent prop
	wdprop = lwb.getclaims(prop, "P2")
	if bool(wdprop):
		wdprop = wdprop['P2'][0]['mainsnak']['datavalue']['value'].replace("http://www.wikidata.org/entity/","")
		print('Wikidata Prop for LWB prop '+prop+' is: '+wdprop)
	else:
		print('*** No equivalent Wikidata property found for '+prop+'.')
		continue

	for item in lwbitems:
		wdqid = item['wdqid']['value'].replace("http://www.wikidata.org/entity/","")
		lwbqid = item['item']['value'].replace("http://data.lexbib.org/entity/","")
		print('\nWill now update LWB item: '+lwbqid+' from wdItem: '+wdqid)
		done = False
		while (not done):
			try:
				request = wikidata.get('wbgetclaims', entity=wdqid, property=wdprop)
			except Exception as ex:
				print('Getclaims operation failed, will try again...\n'+str(ex))
				time.sleep(4)
			if "claims" in request:
				done = True
		if bool(request['claims']):
			for claim in request['claims'][wdprop]:
				dtype = claim['mainsnak']['datavalue']['type']

				if dtype == "wikibase-entityid":
					wdqid = claim['mainsnak']['datavalue']['value']['id']
					value = lwb.wdqid2lwbqid(wdqid)
					#value = json.dumps({"entity-type":"item","numeric-id":lwbqidnum})
					if value == False:
						print('No LWB item found for Wikidata '+wdqid+'. Skipped...')
						continue
				elif dtype == "string":
					value = claim['mainsnak']['datavalue']['value']

				statement = lwb.updateclaim(lwbqid,prop,value,dtype)





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
