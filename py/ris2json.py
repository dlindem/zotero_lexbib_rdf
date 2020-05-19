# converts RIS into JSON, by dlindem
import re
import json


with open('D:/LexikosMerge/Lexikos.ris', 'r', encoding="utf-8") as risfile:
    ris = risfile.read()

risjson = []
risobjects = ris.split('\nER  - \n')
for risobject in risobjects:
    risdict = {}
    rislines = risobject.split('\n')
    for risline in rislines:
        try:
            splitline = risline.split('  - ',1)
            riskey = splitline[0]
            risvalue = splitline[1]
            if riskey in risdict:
                risdict[riskey].append(risvalue)
            else:
                risdict[riskey] = [risvalue]
        except IndexError:
            pass
        #risdict['ER']=''
        #    riskey = "ER"
        #    risvalue = ""
        #print(riskey+risvalue)
    risjson.append(risdict)
print(risjson)

with open('D:/LexikosMerge/convertedris.json', 'w', encoding="utf-8") as json_file:
	json.dump(risjson, json_file, ensure_ascii=False, indent=2)
