# creates descriptions for all instances of a class
import time
import requests
import lwb

classqid = "Q5"
wikilang = "en"
description = "a Person"

print('Will now get a list of all instances of class '+classqid)

url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20%2a%20where%0A%7B%0A%3Furi%20ldp%3AP5%20lwb%3A"+classqid+".%0A%20%20%7D"
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

print('Found '+str(len(bindings))+' instances.\n')
time.sleep(3)

count = 0
for item in bindings:
	count +=1
	lwbitem = item['uri']['value'].replace("http://data.lexbib.org/entity/","")
	desc = lwb.setdescription(lwbitem,wikilang,description)
	if desc:
		print('OK. '+str(len(bindings)-count)+' items left.\n')
