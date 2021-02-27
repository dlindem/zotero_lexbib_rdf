import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import lwb
import time
import re

orphaned = ""

# get issn that are still not linked to an lwb journal ("orphaned issn")
url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20distinct%20%3Fissn%20%20where%0A%7B%20%3Fs%20ldp%3AP20%20%3Fissn%20.%0A%20MINUS%20%7B%3Fjournal%20ldp%3AP5%20lwb%3AQ20%3B%0A%20%20%20%20%20%20%20%20%20%20ldp%3AP20%20%3Fissn.%7D%0A%20%20%0A%7D%20"
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

for item in bindings:
	issn = item['issn']['value']
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='LexBib-Bibliodata-enrichment-script (lexbib.org)')
	sparql.setQuery('SELECT ?journal ?journalLabel WHERE {?journal wdt:P236 '+'"'+issn+'"'+'. SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}')
	sparql.setReturnFormat(JSON)
	success = 0
	try:
		time.sleep(1.5)
		wddict = sparql.query().convert()
		datalist = wddict['results']['bindings']
		print('\nGot ISSN '+issn+' data from Wikidata.')
		wdqid = datalist[0]['journal']['value']
		label = datalist[0]['journalLabel']['value']
		success = 1
		regexp = re.compile(r'Q\d+')
		if regexp.search(label):
			label = ""

	except Exception as ex:
		print("ISSN "+issn+" not found on wikidata, skipping, will add to orphaned list.")
		orphaned += issn+'\tnot found on wikidata.\n'
		continue

	# create lwb serial for this orphaned issn
	lwbqid = lwb.getqid("Q20", wdqid) # for serials, wdqid is also lexbib uri
	statement = lwb.updateclaim(lwbqid, "P3", wdqid, "url")
	statement = lwb.updateclaim(lwbqid, "P20", issn, "string")
	statement = lwb.updateclaim(lwbqid, "P4", wdqid, "url")
	statement = lwb.setlabel(lwbqid, "en", label)

	# add P46 "contained in serial" to bibitems with that issn
	# get bibitems
	
	url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0A%0Aselect%20%3FbibItem%20%3Fissn%20%3Fjournal%20where%0A%7B%20%3FbibItem%20ldp%3AP5%20lwb%3AQ3%20.%0A%20%20%3FbibItem%20ldp%3AP20%20%3Fissn%20.%0A%20%3Fjournal%20ldp%3AP5%20lwb%3AQ20%20.%0A%20%3Fjournal%20ldp%3AP20%20%3Fissn%20.%0A%20FILTER%20%28%3Fissn%20%3D%20%22"+issn+"%22%29%7D"
	done = False
	while (not done):
		try:
			r2 = requests.get(url)
			bindings2 = r2.json()['results']['bindings']
		except Exception as ex:
			print('Error: SPARQL request failed: '+str(ex))
			time.sleep(2)
			continue
		done = True
	print(str(bindings2))

	for item in bindings2:
		bibitem = item['bibItem']['value'].replace("http://data.lexbib.org/entity/","")
		journal = item['journal']['value'].replace("http://data.lexbib.org/entity/","")
		statement = lwb.updateclaim(bibitem,"P46",journal,"item")

with open('D:/LexBib/journals/orphaned_issn.txt', 'w', encoding="utf-8") as orphlist:
	orphlist.write(orphaned)


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
