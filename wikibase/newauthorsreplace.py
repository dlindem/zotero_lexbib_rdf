import csv
import json
import re
# from wikidataintegrator import wdi_core, wdi_login
import config
import lwb
import time

#
# lwbuser = "DavidL"
# with open('D:/LexBib/wikibase/data_lexbib_org_pwd.txt', 'r', encoding='utf-8') as pwdfile:
# 	lwbpass = pwdfile.read()
# mediawiki_api_url = "https://data.lexbib.org/w/api.php"
# sparql_endpoint_url = "https://data.lexbib.org/query/sparql"
# login = wdi_login.WDLogin(lwbuser, lwbpass, mediawiki_api_url=mediawiki_api_url)
# lwbEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)

with open(config.datafolder+'wikibase/newauthors_qid_last.jsonl', encoding="utf-8") as f:
	data = f.read().split('\n')

guidfix = re.compile(r'^(Q\d+)\-')
count = 1
for row in data:
	print('\nCreator ['+str(count)+'], '+str(len(data)-count)+' creators left.')
	item = json.loads(row)
	creatorqid = list(item.keys())[0]
	print('Now processing creator: '+creatorqid+', '+item[creatorqid]['prefLabel'])
	bibItems = item[creatorqid]['bibItems']
	print('We have '+str(len(bibItems))+' publications for this creator.')
	for bibItem in bibItems:
		oldStatement = re.sub(guidfix, r'\1$', bibItem['statementID'])
		lwbqid = re.search(guidfix, bibItem['statementID']).group(1)
		print(lwbqid, oldStatement)
		claim = lwb.getclaimfromstatement(oldStatement)
		if "P39" in claim:
			newprop = "P12"
			listpos = claim["P39"][0]['qualifiers']["P33"][0]['datavalue']['value']
		elif "P42" in claim:
			newprop = "P13"
			listpos = claim["P42"][0]['qualifiers']["P33"][0]['datavalue']['value']
		else:
			print('*** Something is wrong with this supposed creator literal statement')
			time.sleep(10)

		newStatement = lwb.updateclaim(lwbqid,newprop,creatorqid,"item")
		lwb.setqualifier(lwbqid,newprop,newStatement,"P33",listpos,"string")
		lwb.setqualifier(lwbqid,newprop,newStatement,"P67",bibItem["fullName"],"string")

		lwb.removeclaim(oldStatement)
	count +=1
