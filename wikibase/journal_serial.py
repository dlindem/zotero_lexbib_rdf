import json
import lwb

with open('D:/LexBib/journals/article_issn.json', encoding="utf-8") as f:
	itemdict =  json.load(f)
with open('D:/LexBib/journals/issn_journals.json', encoding="utf-8") as f:
	journaldict =  json.load(f)
issndict = {}
for journal in journaldict:
	issndict[journal['issn']] = journal['journal'].replace("http://data.lexbib.org/entity/","")

count = 0
for item in itemdict:
	count += 1
	lwbqid = item['item'].replace("http://data.lexbib.org/entity/","")
	lwb.updateclaim(lwbqid,"P46",issndict[item['issn']],"item")

	print('OK. '+str(len(itemdict)-count)+' items left.')
