# creates descriptions for all instances of a class
import time
import requests
import lwb

descriptions = {
"Q5":"a Person",
"Q8":"a Language",
"Q21":"a journal article",
"Q19":"a conference paper",
"Q25":"a presentation video",
"Q9":"a Place",
"Q17":"a book chapter",
"Q16":"a book",
"Q57":"a thesis",
"Q47":"a presentation",
"Q6":"an Event",
"Q11":"an Organization",
"Q20":"a Journal",
"Q7":"a Term",
"Q8654":"a Country",
"Q1907":"a serial publication volume"
}

wikilang = "en"

for classqid in descriptions:
	description = descriptions[classqid]
	print('Will now get a list of all those instances of class '+classqid+' that have no description.')

	url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20%3Furi%20%3Fdesc%20where%0A%7B%0A%3Furi%20ldp%3AP5%20lwb%3A"+classqid+".%0A%20%20FILTER%20NOT%20EXISTS%20%7B%3Furi%20schema%3Adescription%20%3Fdesc%7D%0A%20%20%7D"
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
