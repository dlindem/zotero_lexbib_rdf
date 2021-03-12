# gets wikidata qid for places, and adds it to the lwb place (if still missing)

from SPARQLWrapper import SPARQLWrapper, JSON
import time
import requests
import lwb

url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20%28substr%28str%28%3Flwbplace%29%2C31%29%20as%20%3Flwb_qid%29%20%3Fwd_url%20where%0A%7B%20%3Flwbplace%20ldp%3AP5%20lwb%3AQ9%20%3B%20%23%20places%0A%20%20%20%20%20%20%20%20%20%20%20%20ldp%3AP3%20%3Flexbib_uri%20.%0A%20%20SERVICE%20%3Chttps%3A%2F%2Fquery.wikidata.org%2Fsparql%3E%20%7B%0A%20%20%20%20%3Flexbib_uri%20schema%3Aabout%20%3Fwd_url%20.%0A%20%20%20%20%3Flexbib_uri%20schema%3AisPartOf%20%3Chttps%3A%2F%2Fen.wikipedia.org%2F%3E%20.%0A%20%20%20%20%0A%20%20%20%20%7D%0A%20%0A%20FILTER%20NOT%20EXISTS%20%7B%0A%20%20%20%20%3Flwbplace%20ldp%3AP4%20%3Fwditem%20.%7D%0A%7D%0A"
done = False
while (not done):
	try:
		r = requests.get(url)
		mappings = r.json()['results']['bindings']
	except Exception as ex:
		print('Error: SPARQL request failed: '+str(ex))
		time.sleep(2)
		continue
	done = True
print(str(mappings))

for mapping in mappings:
	lwb_qid = mapping['lwb_qid']['value']
	wd_url = mapping['wd_url']['value']
	lwb.stringclaim(lwb_qid,"P4",wd_url)
