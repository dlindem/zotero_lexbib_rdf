from tkinter import Tk
from tkinter.filedialog import askopenfilename
import time
import sys
import json
import re
import litprops
import itemprops

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

	lwb_item = {"lexbibUri":lexbibUri,"props":[]}
	for property in item:
		#print(property)
		itemproplist = itemprops.getWbProp(property,item[property])
		litproplist = litprops.getWbProp(property,item[property])
		if litproplist != None:
			lwb_item["props"].append(litproplist)
		if itemproplist != None:
			lwb_item["props"].append(itemproplist)



	lwb_data.append(lwb_item)

#print(str(json.dumps(lwb_data)))
with open(infile.replace('.json', '_lwb_import_data.json'), 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(lwb_data, json_file, indent=2)
	print("\n=============================================\nCreated processed JSON file "+infile.replace('.json', '_lwb_import_data.json')+". Finished.")
