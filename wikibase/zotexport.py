from tkinter import Tk
from tkinter.filedialog import askopenfilename
import time
import sys
import json
import re
import unidecode
import requests
import urllib.parse
import mwclient
import lexvomapping

# LexBib wikibase OAuth
site = mwclient.Site('data.lexbib.org')
with open('D:/LexBib/wikibase/data_lexbib_org_pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()
def get_token():
	login = site.login(username='DavidL', password=pwd)
	csrfquery = site.api('query', meta='tokens')
	token=csrfquery['query']['tokens']['csrftoken']
	print("Got fresh CSRF token.")
	return token
token = get_token()

# Load known qid-lexbibUri mappings
knownqid = {}
try:
	with open('D:/LexBib/wikibase/knownqid.jsonl', encoding="utf-8") as f:
		mappings = f.readlines()
		for mapping in mappings:
			try:
				mapping = mapping.json()
				knownqid[mapping['lexbibItem']] = mapping['qid']
			except:
				pass

except Exception as ex:
	print ('Error: knownqid file does not exist. Will start a new one.')
	print (str(ex))

def save_knownqid(mapping):
	with open('D:/LexBib/wikibase/knownqid.jsonl', 'a', encoding="utf-8") as jsonl_file:
		jsonl_file.write(json.dumps(mapping)+'\n')

# function for item creation (after check if it is known)
def getqid(lwbclass, lexbibItem, token):

	if lexbibItem in knownqid:
		print(lexbibItem+' is a known wikibase item: Qid '+knownqid[lexbibItem]+', no need to create it.')
		return knownqid[lexbibItem]
	else:
		lexbibItemSafe = urllib.parse.quote(lexbibItem, safe='~', encoding="utf-8", errors="strict")
		url = "https://data.lexbib.org/query/sparql?format=json&query=SELECT%20%3FlwbItem%20%0AWHERE%20%0A%7B%20%20%3FlwbItem%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2FP5%3E%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F"+lwbclass+"%3E.%20%0A%0A%20%20%20%3FlwbItem%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2FP3%3E%20%3C"+lexbibItemSafe+"%3E%20.%0A%7D"
		done = False
		while (not done):
			try:
				r = requests.get(url)
				results = r.json()['results']['bindings']
			except Exception as ex:
				print('Error: SPARQL request failed.')
				time.sleep(2)
				continue
			done = True
		if len(results) == 0:
			print('*** Found no Qid for LexBib URI '+lexbibItem+', will create it.')
			claim = {"claims":[
			#{"mainsnak":{"snaktype":"value","property":"P5","datavalue":{"value":lwbclass,"type":"WikibaseItem"}},"type":"statement","rank":"normal"},
			{"mainsnak":{"snaktype":"value","property":"P3","datavalue":{"value":lexbibItem,"type":"string"}},"type":"statement","rank":"normal"}
			]}
			#token = get_token()
			done = False
			while (not done):
				try:
					itemcreation = site.post('wbeditentity', token=token, new="item", bot=True, data=json.dumps(claim))
				except Exception as ex:
					print(str(ex))
					if 'Invalid CSRF token.' in str(ex) or 'referenced before assignment' in str(ex):
						print('Wait a sec. Must get a new CSRF token...')
						token = get_token()
					else:
						time.sleep(4)
					continue
				#print(str(itemcreation))
				if itemcreation['success'] == 1:
					done = True
					qid = itemcreation['entity']['id']
					print('Item creation for '+lexbibItem+': success. QID = '+qid)
				else:
					print('Item creation failed, will try again...')
					time.sleep(2)
			done = False
			while (not done):
				claim = {"entity-type":"item","numeric-id":int(lwbclass.replace("Q",""))}
				classclaim = site.post('wbcreateclaim', token=token, entity=qid, property="P5", snaktype="value", value=json.dumps(claim))
				if classclaim['success'] == 1:
					done = True
					print('Claim creation for '+lexbibItem+': success. Class = '+lwbclass)
					knownqid[lexbibItem] = qid
					save_knownqid({"lexbibItem:":lexbibItem,"qid":qid})
					return qid
				else:
					print('Claim creation failed, will try again...')
					time.sleep(2)
		elif len(results) > 1:
			print('*** Error: Found more than one Wikibase item for one LexBib URI that should be unique... will take the first result.')
			qid = results[0]['lwbItem']['value'].replace("http://data.lexbib.org/entity/","")
			knownqid[lexbibItem] = qid
			save_knownqid({"lexbibItem:":lexbibItem,"qid":qid})
			return qid
		elif len(results) == 1:
			qid = results[0]['lwbItem']['value'].replace("http://data.lexbib.org/entity/","")
			knownqid[lexbibItem] = qid
			print('Found '+lexbibItem+' not in knownqid file but on data.lexbib: Qid '+qid+'; no need to create it, will add to knownqid file.')
			save_knownqid({"lexbibItem:":lexbibItem,"qid":qid})
			return qid


# open and load input file
print('Please select Zotero export JSON to be processed.')
#time.sleep(2)
Tk().withdraw()
infile = askopenfilename()
print('This file will be processed: '+infile)
try:
	with open(infile, encoding="utf-8") as f:
		data =  json.load(f)
except Exception as ex:
	print ('Error: file does not exist.')
	print (str(ex))
	sys.exit()

lwb_data = []
item_updates = []
itemcount = 0
for item in data:
	itemcount += 1
	print("\nItem ["+str(itemcount)+"]: "+item['title'])
	lexbibUri = ""
	if "archive_location" in item:
		if item["archive_location"].startswith('http') == True:
			lexbibUri = re.sub('/+$',"",item["archive_location"]) # use archiveLocation field content (starting with http), removing any slashes at the end
		elif item["archive_location"].startswith('isbn:') == True:
			lexbibUri = re.sub(r'^isbn:','http://worldcat.org/isbn/',item["archive_location"].replace("-",""))
		elif item["archive_location"].startswith('oclc:') == True:
			lexbibUri = re.sub(r'^oclc:','http://worldcat.org/oclc/',item["archive_location"].replace("-",""))
		else:
			lexbibUri = "http://lexbib.org/lexbib/item#"+item["archive_location"]
	if "DOI" in item:
		doi = item['DOI']
		if doi[:4] == "doi:":
			doi = doi[4:]
		elif doi[:8] == "urn:doi:":
			doi = doi[8:]
		elif doi[:9] == "info:doi/":
			doi = doi[9:]
		elif doi[:18] == "http://dx.doi.org/":
			doi = doi[18:]
		elif doi[:15] == "http://doi.org/":
			doi = doi[15:]
		doiurl = "http://doi.org/"+doi
		item["DOI"] = doiurl
		if lexbibUri == "":
			lexbibUri = doiurl
	if lexbibUri == "":
		if item['type'] == "book" or item['type'] == "thesis":
			if "ISBN" in item:
				lexbibUri = "http://worldcat.org/isbn/"+re.search(r'^\d+', item["isbn"].replace("-","")).group(0)
		elif item['type'] == "chapter" or item['type'] == "paper-conference":
			if "ISBN" in item and "page" in item:
				lexbibUri = "http://lexbib.org/lexbib/item#"+re.search(r'^\d+', item["ISBN"].replace("-","")).group(0)+"_"+item["page"].split('-')[0]
		elif "URL" in item:
			lexbibUri = re.sub('/$','',item["URL"]) # use URL field content removing slash at the end
	if lexbibUri == "":
		print('*** ERROR: Could not define lexbib Uri for '+item['title']+'. Item SKIPPED!!!')
		continue
	else:
		print('lexbib Uri will be: '+lexbibUri)

	propvals = []
	for zp in item: # zp: zotero property
		val = item[zp]
		#print(property)
		# itemproplist = itemprops.getWbProp(property,item[property],item['type'])
		# litproplist = litprops.getWbProp(property,item[property],item['type'])
		# if litproplist != None:
		# 	lwb_item["props"].append(litproplist)
		# if itemproplist != None:
		# 	lwb_item["props"].append(itemproplist)

		if zp == "type":

			# props with item value

			if val == "paper-conference":
				propvals.append({"property":"P5","qid":"Q19"})
			elif val == "article-journal":
				propvals.append({"property":"P5","qid":"Q21"})
			elif val == "book":
				propvals.append({"property":"P5","qid":"Q16"})
			elif val == "chapter":
				propvals.append({"property":"P5","qid":"Q17"})
			elif val == "motion_picture": # videos
				propvals.append({"property":"P5","qid":"Q25"})
			elif val == "speech":
				propvals.append({"property":"P5","qid":"Q47"})
			elif val == "thesis":
				propvals.append({"property":"P5","qid":"Q57"})

		elif zp == "tags":
			for tag in val:
				if tag["tag"].startswith(':event ') == True:
					event = tag["tag"].replace(":event ","http://lexbib.org/events#")
					qid = getqid("Q6", event, token)
					propvals.append({"property":"P36","qid":qid})
				if tag["tag"].startswith(':container ') == True:
					container = tag["tag"].replace(":container ","")
					if container.startswith('isbn:') or container.startswith('oclc:'):
						container = container.replace("-","")
						container = container.replace("isbn:","http://worldcat.org/isbn/")
						container = container.replace("oclc:","http://worldcat.org/oclc/")
					elif container.startswith('doi:'):
						container = container.replace("doi:", "http://doi.org/")

					if item['type'] == "article-journal":
						qid = getqid("Q1907", container, token)
					else:
						qid = getqid("Q12", container, token)
					propvals.append({"property":"P9","qid":qid}) # container relation

				if tag["tag"].startswith(':type ') == True:
					type = tag["tag"].replace(":type ","")
					if type == "Review":
						propvals.append({"property":"P5","qid":"Q15"})
					elif type == "Report":
						propvals.append({"property":"P5","qid":"Q46"})
					elif type == "Proceedings":
						propvals.append({"property":"P5","qid":"Q18"})
		elif zp == "language":
			language = lexvomapping.getLexvoId(val)
			qid = getqid("Q8", language, token)
			propvals.append({"property":"P11","qid":qid})

		### props with literal value

		elif zp == "title":
			propvals.append({"property":"P6", "string":val})
		elif zp == "container-title":
			propvals.append({"property":"P8", "string":val})
		elif zp == "event":
			propvals.append({"property":"P37", "string":val})
		elif zp == "page":
			propvals.append({"property":"P24", "string":val})
		elif zp == "publisher":
			propvals.append({"property":"P34", "string":val})
		elif zp == "DOI":
			if "http" not in val:
				val = "http://doi.org/"+val
			propvals.append({"property":"P17", "string":val})
		elif zp == "ISSN":
			if "-" not in val: # normalize ISSN, remove any secondary ISSN
				val = val[0:4]+"-"+val[4:9]
			propvals.append({"property":"P20", "string":val[:9]})
		elif zp == "ISBN":
			val = val.replace("-","")
			val = re.search(r'^\d+',val).group(0)
			if len(val) == 10:
				propvals.append({"property":"P19", "string":val})
			elif len(val) == 13:
				propvals.append({"property":"P18", "string":val})
		elif zp == "volume" and item['type'] == "article-journal": # volume only for journals (book series also have "volume")
			propvals.append({"property":"P22", "string":val})
		elif zp == "issue" and item['type'] == "article-journal": # issue only for journals
			propvals.append({"property":"P23", "string":val})
		elif zp == "id":
			val = "http://lexbib.org/zotero/"+re.search(r'items/(.*)', val).group(1)
			propvals.append({"property":"P16", "string":val})
		elif zp == "URL":
			propvals.append({"property":"P21", "string":val})
		elif zp == "issued":
			year = val["date-parts"][0][0]
			propvals.append({"property":"P14", "string":year})
		elif zp == "author" or zp == "editor":
			if zp == "author":
				prop = "P39"
			elif zp == "editor":
				prop = "P42"
			creators = []
			listpos = 1
			for creator in val:
				if "non-dropping-particle" in creator:
					creator["family"] = creator["non-dropping-particle"]+" "+creator["family"]
				propvals.append({"property":prop, "string":creator["given"]+" "+creator["family"],"Qualifiers":{"P33":str(listpos),"P40":creator["given"],"P41":creator["family"]}})
				listpos += 1




	lwb_data.append({"lexbibUri":lexbibUri,"propvals":propvals})

#print(str(json.dumps(lwb_data)))
with open(infile.replace('.json', '_lwb_import_data.json'), 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(lwb_data, json_file, indent=2)
	print("\n=============================================\nCreated processed JSON file "+infile.replace('.json', '_lwb_import_data.json')+". Finished.")
