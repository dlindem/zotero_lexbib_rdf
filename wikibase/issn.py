import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import lwb
import time



#get issn from lwb
url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX lwb%3A <http%3A%2F%2Fdata.lexbib.org%2Fentity%2F>%0APREFIX ldp%3A <http%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F>%0APREFIX lp%3A <http%3A%2F%2Fdata.lexbib.org%2Fprop%2F>%0APREFIX lps%3A <http%3A%2F%2Fdata.lexbib.org%2Fprop%2Fstatement%2F>%0APREFIX lpq%3A <http%3A%2F%2Fdata.lexbib.org%2Fprop%2Fqualifier%2F>%0A%0Aselect distinct %3Fissn where%0A{ %3Fs ldp%3AP20 %3Fissn .%0A%20 %0A}%20"
done = False
while (not done):
	try:
		r = requests.get(url)
		bindings = r.json()['results']['bindings']
	except Exception as ex:
		print('Error: SPARQL request failed: '+str(ex))
		time.sleep(2)
		continue
	done = True
print(str(bindings))

for journal in bindings:
	issn = journal['issn']['value']
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='LexBib-Bibliodata-enrichment-script (lexbib.org)')
	sparql.setQuery('SELECT ?journal ?journalLabel WHERE {?journal wdt:P236 '+'"'+issn+'"'+'. SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}')
	sparql.setReturnFormat(JSON)

	try:
		time.sleep(1.5)
		wddict = sparql.query().convert()
		datalist = wddict['results']['bindings']
		print('\nGot ISSN '+issn+' data from Wikidata.')
		wdqid = datalist[0]['journal']['value']
		label = datalist[0]['journalLabel']['value']
	except Exception as ex:
		print("ISSN "+issn+" not found on wikidata, skipping. >> "+str(ex))

	lwbqid = lwb.getqid("Q20", wdqid)
	statement = lwb.updateclaim(lwbqid, "P3", "http://lexbib.org/items#issn"+issn, "url")


	# statement = lwb.getclaims(lwbqid, "P4")
	# if bool(statement):
	# 	print("Statement is already there: "+statement["P4"][0]['id'])
	# else:
	# 	statement = lwb.stringclaim(lwbqid, "P4", wdqid)
	#
	# statement = lwb.setlabel(lwbqid, "en", label)
	#
	# statement = lwb.getclaims(lwbqid, "P20")
	# if bool(statement):
	# 	print("Statement is already there: "+statement["P20"][0]['id'])
	# else:
	# 	statement = lwb.stringclaim(lwbqid, "P20", issn)
