import mwclient
import json
from datetime import datetime
site = mwclient.Site('lexbib.wiki.opencura.com')

with open('D:/LexBib/wikibase/pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()

login = site.login(username='DavidL', password=pwd)
#print(login)
csrfquery = site.api('query', meta='tokens')
#print (str(csrfquery))
token=csrfquery['query']['tokens']['csrftoken']

with open('D:/LexBib/wikibase/new_statements.json', encoding="utf-8") as f:
	triples =  json.load(f)

for triple in triples:
	qid=triple['subjectqid']
	prop=triple['property']

	if triple['object']['type'] == "literal":
		object='"'+triple['object']['value']+'"'
		#print('Triple: '+qid+' ('+prop+') '+object)
		#results = site.api('wbeditentity', token=token, id=qid, data={"claims":[{"mainsnak":{"snaktype":"value","property":prop,"datavalue":{"value":object,"type":"string"}},"type":"statement","rank":"normal"}]})
		results = site.post('wbcreateclaim', token=token, entity=qid, property=prop, snaktype="value", value=object)
	elif triple['object']['type'] == "item":
		pass
		results = site.post('wbcreateclaim', token=token, entity=qid, property=prop, snaktype="value", value='{"entity-type":"item","numeric-id":'+object.replace("Q","")+'}')
	if results['success'] == 1:
		print('Wbsetclaim for '+qid+' ('+prop+') '+object+': success.')
	else:
		print('Wbsetclaim for '+qid+' ('+prop+') '+object+': ERROR.')
