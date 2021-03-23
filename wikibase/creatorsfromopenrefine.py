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
		#print(str(item))
		bibItem = item['bibItem'].replace("http://data.lexbib.org/entity/","")
		print('BibItem is '+bibItem+'.')
		oldStatement = re.sub(guidfix, r'\1$', item['statement_id'])
		bibitemqid = re.search(guidfix, item['statement_id']).group(1)
		if 'Qid' in item and item['Qid'].startswith("Q"):
			creatorqid = item['Qid']
			creatorPrefLabel = lwb.getlabel(creatorqid, "en")
			print('This is a known creator item: '+creatorqid+' '+creatorPrefLabel)
		else:
			print('We have no item for author '+item['creatorName']+', will set up a new item.')
			creatorqid = lwb.newitemwithlabel("Q5", "en", item['creatorName'])
			creatorPrefLabel = item['creatorName']
			lwb.updateclaim(creatorqid,"P40",item['firstName'],"string")
			lwb.updateclaim(creatorqid,"P41",item['lastName'],"string")
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

		newStatement = lwb.updateclaim(bibitemqid,newprop,creatorqid,"item")
		lwb.setqualifier(bibitemqid,newprop,newStatement,"P33",listpos,"string")
		lwb.setqualifier(bibitemqid,newprop,newStatement,"P67",item["firstName"]+" "+item["lastName"],"string")
		if creatorPrefLabel != item['firstName']+" "+item['lastName']:
			lwb.setlabel(creatorqid,"en",item['firstName']+" "+item['lastName'],type="alias")
		lwb.removeclaim(oldStatement)





		time.sleep(1)
		count +=1
