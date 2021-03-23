import time
import requests
import lwb

print('Will now get journal issue data...')

url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fqualifier%2F%3E%0A%23%20%28group_concat%28%28strafter%28%3Fbibitem%2C%22http%3A%2F%2Fdata.lexbib.org%2Fentity%2F%22%29%29%3B%20separator%20%3D%20%22%40%22%29%20as%20%3Fbibitems%29%0Aselect%20distinct%20%3Fissue%20%3Fissuelabel%20%3Fissn%20%3Fjournal%20%3Fjournallabel%20%28group_concat%28%28strafter%28str%28%3Fbibitem%29%2C%22http%3A%2F%2Fdata.lexbib.org%2Fentity%2F%22%29%29%3B%20separator%20%3D%20%22%40%22%29%20as%20%3Fbibitems%29%20where%0A%7B%3Fissue%20ldp%3AP5%20lwb%3AQ1907%20.%0A%20%3Fissue%20rdfs%3Alabel%20%3Fissuelabel%20.%0A%20%3Fbibitem%20ldp%3AP9%20%3Fissue%20.%0A%20%3Fbibitem%20ldp%3AP20%20%3Fissn%20.%0A%20%3Fjournal%20ldp%3AP5%20lwb%3AQ20%20.%0A%20%3Fjournal%20ldp%3AP20%20%3Fissn%20.%0A%20%3Fjournal%20rdfs%3Alabel%20%3Fjournallabel%20.%0A%0A%20%20%7D%0AGROUP%20BY%20%3Fissue%20%3Fissuelabel%20%3Fissn%20%3Fjournal%20%3Fjournallabel%20%3Fbibitems"

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
#print(str(bindings))

print('Found '+str(len(bindings))+' journal issues...\n')
time.sleep(3)

count = 0
for item in bindings:
	count +=1
	issueqid = item['issue']['value'].replace("http://data.lexbib.org/entity/","")
	issn = item['issn']['value']
	lwb.updateclaim(issueqid,"P20",issn,"string")
	journalqid = item['journal']['value'].replace("http://data.lexbib.org/entity/","")
	lwb.updateclaim(issueqid,"P46",journalqid,"item")

	for bibitem in item['bibitems']['value'].split('@'):
			lwb.updateclaim(bibitem,"P46",journalqid,"item")
	print('OK. '+str(len(bindings)-count)+' items left.\n')
