from SPARQLWrapper import SPARQLWrapper, JSON
import time
import sys
import requests
import mwclient
import lwb

# class if items to be enriched from Wikidata, example "Q8" for language
c = "Q8"
# List of LWB properties to be taken values for from Wikidata
props = [
"P43" # Wikimedia Language Code
]

wdclass = lwb.getclaims(c, "P4")
if bool(wdclass):
	wdclass = wdclass['P4'][0]['mainsnak']['datavalue']['value'].replace("http://www.wikidata.org/entity/","")
	print(wdclass)
else:
	print('*** No equivalent Wikidata item found for '+c+'.')
	sys.exit()

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
		print(wdprop)
	else:
		print('*** No equivalent Wikidata property found for '+prop+'.')
		continue

	for item in lwbitems:
		wdqid = item['wdqid']['value'].replace("http://www.wikidata.org/entity/","")
		lwbqid = item['item']['value'].replace("http://data.lexbib.org/entity/","")
		done = False
		while (not done):
			try:
				request = wikidata.get('wbgetclaims', entity=wdqid, property=wdprop)
				if "claims" in request:
					done = True
			except Exception as ex:
				print('Getclaims operation failed, will try again...\n'+str(ex))
				time.sleep(4)
			if bool(request['claims']):
				value = request['claims'][wdprop][0]['mainsnak']['datavalue']['value']
				#print(lwbqid+prop+value)
				statement = lwb.stringclaim(lwbqid,prop,value)





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
