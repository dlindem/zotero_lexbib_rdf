import json
import lwb


propmap = {
"http://www.w3.org/2004/02/skos/core#broader": "P72",
"http://www.w3.org/2004/02/skos/core#inScheme": "P74",
"http://www.w3.org/2004/02/skos/core#narrower": "P73",
"http://www.w3.org/2004/02/skos/core#topConceptOf": "P75",
"http://www.w3.org/2004/02/skos/core#note": "P81",
"http://www.w3.org/2004/02/skos/core#related": "P76",
"http://www.w3.org/2004/02/skos/core#closeMatch": "P77",
"http://www.w3.org/2004/02/skos/core#exactMatch": "P78",
"http://www.w3.org/2004/02/skos/core#relatedMatch": "P79",
"http://www.w3.org/2004/02/skos/core#definition": "P80"
}

with open('D:/LexBib/terms/SKOS4lwb.json', encoding="utf-8") as f:
	data =  json.load(f)['results']['bindings']

count = 1
for row in data:
	print('\nTriple ['+str(count)+'], '+str(len(data)-count)+' triples left.')
	lwbs = lwb.getqid("Q7", row['s']['value'])

	if row['p']['value'] in propmap:
		if row['o']['type'] == "literal":
			statement = lwb.updateclaim(lwbs,propmap[row['p']['value']],row['o']['value'].rstrip(),"string")
		else:
			lwbo = lwb.getqid("Q7", row['o']['value'].rstrip())
			statement = lwb.updateclaim(lwbs,propmap[row['p']['value']],lwbo,"item")
	elif row['p']['value'] == "http://www.w3.org/2004/02/skos/core#prefLabel":
		lwb.setlabel(lwbs, row['o']['xml:lang'], row['o']['value'].rstrip())
	elif row['p']['value'] == "http://www.w3.org/2004/02/skos/core#altLabel":
		lwb.setlabel(lwbs, row['o']['xml:lang'], row['o']['value'].rstrip(), type="alias")
	count += 1
