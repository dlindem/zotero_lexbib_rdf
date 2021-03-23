import time
import requests
import lwb

print('Will now get creator name variants from bibitems...')

url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20lwb%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20distinct%20%3Fauthor%20%3FauthorLabel%20%3Fauthornamevar%20%0Awhere%20%7B%0A%20%20%3Fauthor%20ldp%3AP5%20lwb%3AQ5%20.%0A%20%20%3Fauthor%20rdfs%3Alabel%20%3FauthorLabel%20.%0A%20%20%3FbibItem%20lp%3AP12%20%3Fauthorstatement%20.%0A%20%20%3Fauthorstatement%20lps%3AP12%20%3Fauthor%20.%0A%20%20%3Fauthorstatement%20lpq%3AP67%20%3Fauthornamevar%20.%0A%20%20FILTER%20%28str%28%3Fauthornamevar%29%20%21%3D%20str%28%3FauthorLabel%29%29%0A%20%0A%20%20%0A%20%20%7D%20ORDER%20BY%20%3Fauthor%20%3FauthorLabel%20%3Fauthornamevar%20"

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

print('Found '+str(len(bindings))+' creator name variants (that do not match with the author prefLabel)...\n')
time.sleep(3)

count = 0
for item in bindings:
	count +=1
	creatorqid = item['author']['value'].replace("http://data.lexbib.org/entity/","")
	namevar = item['authornamevar']['value']
	altlabel = lwb.setlabel(creatorqid,"en",namevar,type="alias")
	if altlabel:
		print('OK. '+str(len(bindings)-count)+' namevars left.\n')
