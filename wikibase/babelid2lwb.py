import csv
import json
import requests
import time

import lwb


# get csv (part of google spreadsheet used for manual BabelID annotation)
with open('D:/LexBib/terms/term_bnid_status_labels.csv') as csvfile:
	termdict = csv.DictReader(csvfile)
	termlist = list(termdict)
	print(str(termlist))
	totalrows = len(termlist)
	#print(str(termdict))
	count = 1
	processed = []
	for row in termlist:

		print ('\nNow processing term '+str(count)+' of '+str(totalrows)+': '+row["term"])
		lwbqid = lwb.getqid("Q7",row['term'])
		if row['term'] not in processed and row["status"] != "":
			if row['bnid'].startswith("bn:"):
				statement = lwb.updateclaim(lwbqid, "P86", row['bnid'], "string")
				qualifier = lwb.setqualifier(lwbqid, "P86", statement, "P87", row['status'], "string")
				reference = lwb.setref(statement,"P3", row['term'], "url")
			elif row['bnid'] == "" and row['status'] == "0":
				statement = lwb.updateclaim(lwbqid, "P86", "novalue", "novalue")
				qualifier = lwb.setqualifier(lwbqid, "P86", statement, "P87", "0", "string")
				reference = lwb.setref(statement,"P3", row['term'], "url")
		processed.append(row['term'])
		count +=1
