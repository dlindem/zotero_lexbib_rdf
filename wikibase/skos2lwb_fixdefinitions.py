import json
import lwb
import csv


propmap = {
# "http://www.w3.org/2004/02/skos/core#broader": "P72",
# "http://www.w3.org/2004/02/skos/core#inScheme": "P74",
# "http://www.w3.org/2004/02/skos/core#narrower": "P73",
# "http://www.w3.org/2004/02/skos/core#topConceptOf": "P75",
# "http://www.w3.org/2004/02/skos/core#note": "P81",
# "http://www.w3.org/2004/02/skos/core#related": "P76",
# "http://www.w3.org/2004/02/skos/core#closeMatch": "P77",
# "http://www.w3.org/2004/02/skos/core#exactMatch": "P78",
# "http://www.w3.org/2004/02/skos/core#relatedMatch": "P79",
"http://www.w3.org/2004/02/skos/core#definition": "P80"
}

with open('D:/LexBib/terms/SKOS_defs_fix.csv', encoding="utf-8") as f:
	data =  csv.DictReader(f)

	count = 1
	for row in data:
		print('\nDef ['+str(count)+']: '+row['subject'])
		lwbs = lwb.getqid("Q7", row['subject'])

		statement = lwb.updateclaim(lwbs,"P80",row['def'],"string")
		reference = lwb.setref(statement,"P3",row['subject'],"url")
		# 	lwb.setlabel(lwbs, row['o']['xml:lang'], row['o']['value'].rstrip(), type="alias")
		count += 1
