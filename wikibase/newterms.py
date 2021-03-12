import csv
import json
import lwb
import config

with open(config.datafolder+"/terms/SkE terms for SKOS vocab - batch 1.csv", 'r', encoding="utf-8") as csvfile:
	csvdict = csv.DictReader(csvfile)

	for item in csvdict:
		print(str(item))

		if item['SKOS Concept URI'] != "":
			lwbqid = lwb.getqid("Q7", item['SKOS Concept URI'])
		else:
			lwbqid = lwb.newitemwithlabel("Q7", "en", item['Keyword4newScheme'])

		schemeStatement = lwb.updateclaim(lwbqid,"P74","Q22279","item") # skos:inScheme SkE #1

		scoreStatement = lwb.updateclaim(lwbqid,"P82",item['SkE score'],"string")
		lwb.setqualifier(lwbqid, "P82", scoreStatement, "P83", "Q22279", "item")
