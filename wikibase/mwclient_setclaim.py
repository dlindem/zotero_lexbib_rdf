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


qid="Q109"
prop="P5"
object="Q8"

results = site.post('wbcreateclaim', token=token, entity=qid, property=prop, snaktype="value", value='{"entity-type":"item","numeric-id":'+object.replace("Q","")+'}')
if results['success'] == 1:
	print('Wbsetclaim for '+qid+' ('+prop+') '+object+': success.')
else:
	print('Wbsetclaim for '+qid+' ('+prop+') '+object+': ERROR.')
