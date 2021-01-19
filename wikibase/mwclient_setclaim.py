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


qid="P4"
prop="P29"
time="2018-01-01T02:00:00.000Z"
#{"snaktype":"value","property":"P813","datavalue":{"value":{"time":"+2017-09-05T00:00:00Z","timezone":0,"before":0,"after":0,"precision":11,"calendarmodel":"http://www.wikidata.org/entity/Q1985727"},"type":"time"},"datatype":"time"}

results = site.post('wbcreateclaim', token=token, entity=qid, property=prop, snaktype="value", datatype="time", value='{"type":"time", "time":"+2018-01-01T02:00:00.000Z","timezone":0,"before":0,"after":0,"precision":9, "calendarmodel":"http://www.wikidata.org/entity/Q1985727"}')
if results['success'] == 1:
	print('Wbcreateclaim for '+qid+' ('+prop+') '+time+': success.')
else:
	print('Wbsetclaim for '+qid+' ('+prop+') '+time+': ERROR.')
