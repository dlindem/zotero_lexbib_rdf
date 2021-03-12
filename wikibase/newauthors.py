import csv
import json
from wikidataintegrator import wdi_core, wdi_login
import lwb

lwbuser = "DavidL"
with open('D:/LexBib/wikibase/data_lexbib_org_pwd.txt', 'r', encoding='utf-8') as pwdfile:
	lwbpass = pwdfile.read()
mediawiki_api_url = "https://data.lexbib.org/w/api.php"
sparql_endpoint_url = "https://data.lexbib.org/query/sparql"
login = wdi_login.WDLogin(lwbuser, lwbpass, mediawiki_api_url=mediawiki_api_url)
lwbEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)

# with open('D:/LexBib/wikibase/CreatorNames_18104.csv', encoding="utf-8") as csvfile: # source file
# 	csvdict = csv.DictReader(csvfile)
# 	data = {}
# 	for row in csvdict:
# 		if row['Merging'] != "":
# 			newauthor = row['Merging']
# 			data[newauthor] = {"prefLabel":newauthor,"firstName":row['firstName'],"lastName":row['lastName'],"bibItems":[]}
# 		data[newauthor]['bibItems'].append({"fullName":row['creatorName'],"firstName":row['firstName'],"lastName":row['lastName'],"bibItem":row['bibItem'],"statementID":row['statement_id']})
#
# #print(str(data))
# with open('D:/LexBib/wikibase/newauthors.json', 'w', encoding="utf-8") as targetfile:
# 	json.dump(data, targetfile, indent=2)

with open('D:/LexBib/wikibase/newauthors.json', encoding="utf-8") as f:
	data =  json.load(f)

for author in data:
	lwbdata = []
	lwbdata.append(wdi_core.WDItemID("Q5", prop_nr="P5")) # instance of Person
	lwbdata.append(wdi_core.WDString(data[author]['firstName'], prop_nr="P40")) # first Name
	lwbdata.append(wdi_core.WDString(data[author]['lastName'], prop_nr="P41")) # last Name
	item = lwbEngine(new_item=True, data=lwbdata)
	lwbitem = item.write(login)
	lwb.setlabel(lwbitem, "en", data[author]['prefLabel'])
	result = {lwbitem:data[author]}
	print(str(result))
	with open('D:/LexBib/wikibase/newauthors_qid.jsonl', 'a', encoding="utf-8") as jsonl_file:
		jsonl_file.write(json.dumps(result)+'\n')
