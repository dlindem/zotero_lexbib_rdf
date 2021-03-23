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

with open(config.datafolder+'wikibase/newauthors-23032021.csv', encoding="utf-8") as f:
	data = csv.DictReader(f)

	guidfix = re.compile(r'^(Q\d+)\-')
	count = 1
	for item in data:
		print('\nItem ['+str(count)+'].')
		bibItem = item['bibItem'].replace("http://data.lexbib.org/entity/","")
		print('BibItem is '+bibItem+'.')
		oldStatement = re.sub(guidfix, r'\1$', item['statement_id'])
		if 'Qid' in item and item['Qid'].startswith("Q"):
			lwbqid = re.search(guidfix, item['statement_id']).group(1)
			creatorqid = item['Qid']
			#print(lwbqid, oldStatement)
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
			lwb.setqualifier(lwbqid,newprop,newStatement,"P67",item["firstName"]+" "+item["lastName"],"string")

			lwb.removeclaim(oldStatement)
		else:
			print('We have no item for author '+item['creatorName'])
			time.sleep(1)
		count +=1
