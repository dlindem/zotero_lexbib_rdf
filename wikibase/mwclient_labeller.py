import mwclient
import json
from datetime import datetime
site = mwclient.Site('lexbib.wiki.opencura.com')

with open('D:/LexBib/wikibase/lwd_labels.json', encoding="utf-8") as f:
	labels =  json.load(f)
#print(labels)

with open('D:/LexBib/wikibase/pwd.txt', 'r', encoding='utf-8') as pwdfile:
    pwd = pwdfile.read()

login = site.login(username='DavidL', password=pwd)
#print(login)
csrfquery = site.api('query', meta='tokens')
#print (str(csrfquery))
token=csrfquery['query']['tokens']['csrftoken']

for label in labels:
    value=labels[label]['Len']

    results = site.api('wbsetlabel', id=label, language='en', value=value, token=token)

    for result in results:

        if "success" in result:
            print('Wbsetlabel for '+label+' ('+value+'):'+result)
            labels[label]['updated'] = datetime.now()


with open('D:/LexBib/wikibase/lwd_labels.json', 'w', encoding="utf-8") as json_file:
	json.dump(labels, json_file, ensure_ascii=False, indent=2)
print("\nLexBib Wikibase Item Labels json updated.")
#wbsetlabel&id=Q62&language=es&value=Boston
