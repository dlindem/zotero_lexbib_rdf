import json
import lwb_functions


with open('D:/LexBib/terms/langdict.json', encoding="utf-8") as f:
	langdict =  json.load(f)

count = 0
for lang in langdict:
	count +=1
	print('\nLine ['+str(count)+'] of '+str(len(langdict))+': '+lang)
	qid = lwb_functions.getqid(["Q8"], lang) # class Language
	# statement = lwb_functions.stringclaim(qid, "P4", langdict[lang]['wdqid'])
	# statement = lwb_functions.stringclaim(qid, "P32", lang)
	# for label in langdict[lang]['labels']:
	# 	statement = lwb_functions.setlabel(qid, label, langdict[lang]['labels'][label])


print('\nFinished.\n')
