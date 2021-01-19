# looks for labels that have not been updated in LWB and sets them from source 'lwb_labels.json'

import mwclient
import json
from datetime import datetime
import re
lwb = mwclient.Site('lexbib.wiki.opencura.com')

with open('D:/LexBib/wikibase/lwd_labels.json', encoding="utf-8") as f:
	labels =  json.load(f)
#print(labels)

with open('D:/LexBib/wikibase/pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()

login = lwb.login(username='DavidL', password=pwd)
#print(login)
csrfquery = lwb.api('query', meta='tokens')
#print (str(csrfquery))
token=csrfquery['query']['tokens']['csrftoken']

for qid in labels:
	#print(qid)
	#print(labels[qid])
	for label in labels[qid]:
		#print (label)
		if 'update' not in labels[qid][label]:
			language = re.sub(r'^L|A','',label)
			value=labels[qid][label]['value']
			try:
				if label[0] == "L":
					results = lwb.post('wbsetlabel', id=qid, language=language, value=value, token=token)
				elif label[0] == "A":
					results = lwb.post('wbsetaliases', id=qid, language=language, add=value, token=token)
				for result in results:
					if "success" in result:
						print('Wbsetlabel/alias (Type '+label[0]+') for '+qid+' ('+value+'):'+result)
						labels[qid][label]['update'] = str(datetime.now())
			except Exception as ex:
				labels[qid][label]['update'] = {"error": str(ex)}
				print(str(ex))

with open('D:/LexBib/wikibase/lwd_labels.json', 'w', encoding="utf-8") as json_file:
	json.dump(labels, json_file, ensure_ascii=False, indent=2)
print("\nLexBib Wikibase Item Labels json updated.")
#wbsetlabel&id=Q62&language=es&value=Boston
