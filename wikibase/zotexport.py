from tkinter import Tk
from tkinter.filedialog import askopenfilename
import time
import sys
import json
import re
import unidecode
import os
import shutil
#import requests
#import urllib.parse

import lexvomapping
import lwb

# open and load input file
print('Please select Zotero export JSON to be processed.')
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

# load list of already exported PDFs
try:
	with open('D:/LexBib/exports/exported_PDF.json', 'r', encoding="utf-8") as pdflistfile:
		pdflist = json.load(pdflistfile)
except:
	print('\npdflistfile not there, will save in a new one.')
	pdflist = []

# process Zotero export JSON
token = lwb.get_token()
knownqid=lwb.load_knownqid()
lwb_data = []
#item_updates = []
itemcount = 0
for item in data:
	itemcount += 1
	print("\nItem ["+str(itemcount)+"]: "+item['title'])
	lexbibUri = ""
	lexbibClass = ""

	# define LexBib BibItem URI
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
				lexbibUri = "http://worldcat.org/isbn/"+re.search(r'^\d+', item["ISBN"].replace("-","")).group(0)
		elif item['type'] == "chapter" or item['type'] == "paper-conference":
			if "ISBN" in item and "page" in item:
				lexbibUri = "http://lexbib.org/lexbib/item#"+re.search(r'^\d+', item["ISBN"].replace("-","")).group(0)+"_"+item["page"].split('-')[0]
		elif "URL" in item:
			lexbibUri = re.sub('/$','',item["URL"]) # use URL field content removing slash at the end
	if lexbibUri == "":
		print('*** ERROR: Could not define lexbib Uri for '+item['title']+'. Item SKIPPED!!!')
		lwb.logging.error('Could not define lexbib Uri for '+item['title']+'. Item SKIPPED!!!')
		continue
	else:
		print('lexbib Uri will be: '+lexbibUri)

	# iterate through zotero properties
	creatorvals = []
	propvals = []
	for zp in item: # zp: zotero property
		val = item[zp] # val: value of zotero property

		# lexbib zotero tags can contain statements (shortcode for property, and value).
		# If item as value, and that item does not exist, it is created.
		if zp == "tags":
			for tag in val:
				if tag["tag"].startswith(':event ') == True:
					event = tag["tag"].replace(":event ","")
					if event.startswith('http'): # event uri is from outside lexbib
						qid = lwb.getqid("Q6", event)
					else: # convert to event uri in lexbib events namespace
						qid = lwb.getqid("Q6", 'http://lexbib.org/events#'+event)
					propvals.append({"property":"P36","datatype":"item","value":qid})
				if tag["tag"].startswith(':container ') == True:
					container = tag["tag"].replace(":container ","")
					if container.startswith('isbn:') or container.startswith('oclc:'):
						container = container.replace("-","")
						container = container.replace("isbn:","http://worldcat.org/isbn/")
						container = container.replace("oclc:","http://worldcat.org/oclc/")
					elif container.startswith('doi:'):
						container = container.replace("doi:", "http://doi.org/")

					if item['type'] == "article-journal":
						qid = lwb.getqid("Q1907", container)
					else:
						qid = lwb.getqid("Q12", container)
					if "title-short" in item:
						lwb.setlabel(qid, "en", item['title-short'])
					propvals.append({"property":"P9","datatype":"item","value":qid}) # container relation

				if tag["tag"].startswith(':type ') == True:
					type = tag["tag"].replace(":type ","")
					if type == "Review":
						propvals.append({"property":"P5","datatype":"item","value":"Q15"})
					elif type == "Report":
						propvals.append({"property":"P5","datatype":"item","value":"Q46"})
					elif type == "Proceedings":
						propvals.append({"property":"P5","datatype":"item","value":"Q18"})
					elif type == "Dictionary":
						propvals.append({"property":"P5","datatype":"item","value":"Q31"})
					elif type == "Software":
						lexbibClass = "Q30" # this will override item type "book"

		# Publication language. If language item does not exist, it is created. lexBibUri = lexvo uri
		elif zp == "language":
			language = lexvomapping.getLexvoId(val)
			qid = lwb.getqid("Q8", language)
			propvals.append({"property":"P11","datatype":"item","value":qid})

		elif zp == "type" and lexbibClass == "":

			if val == "paper-conference":
				lexbibClass = "Q19"
			elif val == "article-journal":
				lexbibClass = "Q21"
			elif val == "book":
				lexbibClass = "Q16"
			elif val == "chapter":
				lexbibClass = "Q17"
			elif val == "motion_picture": # videos
				lexbibClass = "Q25"
			elif val == "speech":
				lexbibClass = "Q47"
			elif val == "thesis":
				lexbibClass = "Q57"


		### props with literal value
		elif zp == "id":
			val = "http://lexbib.org/zotero/"+re.search(r'items/(.*)', val).group(1)
			propvals.append({"property":"P16","datatype":"string","value":val})
		elif zp == "title":
			propvals.append({"property":"P6","datatype":"string","value":val})
		elif zp == "container-title":
			propvals.append({"property":"P8","datatype":"string","value":val})
		elif zp == "event":
			propvals.append({"property":"P37","datatype":"string","value":val})
		elif zp == "page":
			propvals.append({"property":"P24","datatype":"string","value":val})
		elif zp == "publisher":
			propvals.append({"property":"P34","datatype":"string","value":val})
		elif zp == "DOI":
			if "http" not in val:
				val = "http://doi.org/"+val
			propvals.append({"property":"P17","datatype":"string","value":val})
		elif zp == "ISSN":
			if "-" not in val: # normalize ISSN, remove any secondary ISSN
				val = val[0:4]+"-"+val[4:9]
			propvals.append({"property":"P20","datatype":"string","value":val[:9]})
		elif zp == "ISBN":
			val = val.replace("-","")
			val = re.search(r'^\d+',val).group(0)
			if len(val) == 10:
				propvals.append({"property":"P19","datatype":"string","value":val})
			elif len(val) == 13:
				propvals.append({"property":"P18","datatype":"string","value":val})
		elif zp == "volume" and item['type'] == "article-journal": # volume only for journals (book series also have "volume")
			propvals.append({"property":"P22","datatype":"string","value":val})
		elif zp == "issue" and item['type'] == "article-journal": # issue only for journals
			propvals.append({"property":"P23","datatype":"string","value":val})
		elif zp == "journalAbbreviation":
			propvals.append({"property":"P54","datatype":"string","value":val})
		elif zp == "URL":
			propvals.append({"property":"P21","datatype":"string","value":val})
		elif zp == "issued":
			year = val["date-parts"][0][0]
			propvals.append({"property":"P14","datatype":"string","value":year})
		elif zp == "edition":
			propvals.append({"property":"P64","datatype":"string","value":val})
		elif zp == "author" or zp == "editor":
			if zp == "author":
				prop = "P39"
			elif zp == "editor":
				prop = "P42"
			listpos = 1
			for creator in val:
				if "literal" in creator: # this means there is no firstname-lastname but a single string (for Orgs):
					pass # TBD
				else:
					if "non-dropping-particle" in creator:
						creator["family"] = creator["non-dropping-particle"]+" "+creator["family"]
					if creator["family"] == "Various":
						creator["given"] = "Various"
					creatorvals.append({"property":prop,"datatype":"string","value":creator["given"]+" "+creator["family"],"Qualifiers":[{"property":"P33","datatype":"string","value":str(listpos)},{"property":"P40","datatype":"string","value":creator["given"]},{"property":"P41","datatype":"string","value":creator["family"]}]})
					listpos += 1

		# Attachments
		elif zp == "attachments":
			for attachment in val:
				if attachment['contentType'] == "application/pdf":
					pdfloc = re.search(r'(D:\\Zotero\\storage)\\([A-Z0-9]+)\\(.*)', attachment['localPath'])
					pdfpath = pdfloc.group(1)
					pdffolder = pdfloc.group(2)
					pdfoldfile = pdfloc.group(3)
					forbidden = re.compile(r'[^a-zA-Z0-9_\.]')
					if forbidden.search(pdfoldfile) != None:
						print("PDF file "+pdfoldfile+" will be renamed (remove [^a-zA-Z0-9_] from name)")
						pdfnewfile = forbidden.sub('', pdfoldfile)
						print('Renamed PDF file to handle is '+pdfnewfile)
						time.sleep(2)
					else:
						pdfnewfile = pdfoldfile
						print('Unrenamed PDF file to handle is '+pdfnewfile)
					if pdffolder not in pdflist:
						newpath = 'D:\\LexBib\\exports\\export_filerepo\\'+pdffolder
						if not os.path.isdir(newpath):
							os.makedirs(newpath)
						shutil.copy(pdfpath+'\\'+pdffolder+'\\'+pdfoldfile, newpath+'\\'+pdfnewfile)
						print('Found and copied '+pdfnewfile)
						pdflist.append(pdffolder)
						propvals.append({"property":"P70","datatype":"string","value":"http://lexbib.org/zotero/"+pdffolder})
				elif attachment['contentType'] == "text/plain":
					txturl = attachment['uri'].replace("http://zotero.org/groups/1892855/items/","http://lexbib.org/zotero/")
					propvals.append({"property":"P71","datatype":"string","value":txturl})

		# Extra field, can contain a wikipedia page title, used in Elexifinder project as first-author-location-URI
		elif zp == "extra":
			place = val.replace("\n","").replace(" ","").split(";")[0]
			if "en.wikipedia" in place:
				# check if this location is already in LWB, if it doesn't exist, create it
				qid = lwb.getqid("Q9", place)
				propvals.append({"property":"P29","datatype":"item","value":qid})

	# add lexbib Class and propvals to target item
	if lexbibClass == "":
		print('*** Item '+lexbibUri+' has not been assigned any LexBib Class, that is fatal.')
		lwb.logging.error('Item '+lexbibUri+' has not been assigned any LexBib Class, that is fatal.')

	lwb_data.append({"lexbibUri":lexbibUri,"lexbibClass":lexbibClass,"creatorvals":creatorvals,"propvals":propvals})

# save updated PDF list
with open('D:/LexBib/exports/exported_PDF.json', 'w', encoding="utf-8") as pdflistfile:
	json.dump(pdflist, pdflistfile, ensure_ascii=False, indent=2)

#print(str(json.dumps(lwb_data)))
with open(infile.replace('.json', '_lwb_import_data.json'), 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(lwb_data, json_file, indent=2)
	print("\n=============================================\nCreated processed JSON file "+infile.replace('.json', '_lwb_import_data.json')+". Finished.")
