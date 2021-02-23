import json
import lwb

with open('D:/LexBib/countries/query.json', encoding="utf-8") as f:
	dict =  json.load(f)

count = 0
for item in dict:
	count += 1
	lwbqid = lwb.getqid("Q8654", item['country'])
	lwb.setlabel(lwbqid, "en", item['countryLabel'])
	lwb.stringclaim(lwbqid, "P4", item['country'])

	print('OK. '+str(len(dict)-count)+' countries left.')
