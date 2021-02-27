import json
import lwb


with open('D:/LexBib/terms/langdict.json', encoding="utf-8") as f:
	langdict =  json.load(f)

with open('D:/LexBib/languages/publangs.txt', encoding="utf-8") as f:
	publangs = f.read().split('\n')

count = 0
for lang in publangs:
	count +=1
	print('\nLine ['+str(count)+'] of '+str(len(publangs))+': '+lang)

	qid = lwb.getqid(["Q8"], lang) # class Language
	statement = lwb.updateclaim(qid, "P4", langdict[lang]['wdqid'],"url")
	statement = lwb.updateclaim(qid, "P32", lang, "url")
	for label in langdict[lang]['labels']:
		statement = lwb.setlabel(qid, label, langdict[lang]['labels'][label])
	print('OK. '+str(len(publangs)-count)+' languages left.')

print('\nFinished.\n')
