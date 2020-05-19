#converts json to ris (json key to ris key, json value to ris value), by dlindem
import json

with open("D:/LexikosMerge/newcomernotmerged.json", encoding="utf-8") as f:
	jsonfile =  json.load(f, encoding="utf-8")

print(jsonfile)

with open('D:/LexikosMerge/newcomernotmergedris.ris', 'w', encoding="utf-8") as risfile:
	for item in jsonfile:
		for key, valuelist in item.items():
			for value in valuelist:
				risfile.write(key+"  - "+value+"\n")
		risfile.write("ER  - \n\n")
