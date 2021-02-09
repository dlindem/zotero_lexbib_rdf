import json


with open('D:/LexBib/languages/langdict.json', encoding="utf-8") as f:
	langdict =  json.load(f)
with open('D:/LexBib/wikibase/lwd_labels.json', encoding="utf-8") as f:
	labels =  json.load(f)

qs = ""

for lang in langdict:
    qs += "CREATE\n"
    qs += "LAST\tP3\t\""+lang+'\"\n'
    qs += "LAST\tP4\t\""+langdict[lang]['wdqid']+'\"\n'
    qs += "LAST\tP5\t"+'Q7\n'
    for label in langdict[lang]['labels']:
        qs += "LAST\tL"+label+'\t\"'+langdict[lang]['labels'][label]+'\"\n'

print (qs)

with open('D:/LexBib/wikibase/languages_create_commands.txt', 'w', encoding='utf-8') as qsfile:
        qsfile.write(qs)

print('\nQuickstatements V1 create commands file written. Finished.\n')
