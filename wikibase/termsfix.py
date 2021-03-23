import json
import lwb

# get output generated with babelterms.py
with open('D:/LexBib/terms/babeltranslations.json', encoding="utf-8") as f:
	babeldict =  json.load(f)

target = {}
for subj in babeldict:
	lwbqid = lwb.getqid("Q7", subj, onlyknown=True)
	target[lwbqid.replace("http://data.lexbib.org/entity/","")] = babeldict[subj]

with open('D:/LexBib/terms/babeltranslations_lwbqid.json', "w", encoding="utf-8") as f:
	json.dump(target, f, indent=2)
