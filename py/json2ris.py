#converts json to ris (json key to ris key, json value to ris value), by dlindem
import json

risjson_input_file = 'D:/LexikosMerge/Rest/mergedris.json'
ris_result_file = 'D:/LexikosMerge/Rest/mergedrestris.ris'

with open(risjson_input_file, encoding="utf-8") as f:
	jsonfile =  json.load(f, encoding="utf-8")

print(jsonfile)

with open(ris_result_file, 'w', encoding="utf-8") as risfile:
	for item in jsonfile:
		for key, valuelist in item.items():
			for value in valuelist:
				risfile.write(key+"  - "+value+"\n")
		risfile.write("ER  - \n\n")
