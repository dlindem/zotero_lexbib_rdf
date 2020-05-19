# joins two RIS-JSON files, common pivot key "AN", by dlindem
import json

pk = 'AN' # pivot key is AN

with open("D:/LexikosMerge/convertedris.json", encoding="utf-8") as f:
	original =  json.load(f, encoding="utf-8")
with open("D:/LexikosMerge/csv2json.json", encoding="utf-8") as f:
	newcomer =  json.load(f, encoding="utf-8")

for origitem in original:
	#print(origitem)
	#print(origitem['AN'])
	for newitem in newcomer:
		if pk in newitem and pk in origitem and str(origitem[pk]) == str(newitem[pk]):
			print('found merge candidate')
			for key, value in origitem.items():
				if key != pk:
					try:
						origitem[key].extend(newitem[key])
					except KeyError:
						pass
			for key, value in newitem.items():
				if origitem.get(key) == None:
					origitem[key] = newitem[key]
			newcomer.remove(newitem) # after merging, delete item from newcomer json



with open('D:/LexikosMerge/mergedris.json', 'w', encoding="utf-8") as json_file:
	json.dump(original, json_file, ensure_ascii=False, indent=2)
with open('D:/LexikosMerge/newcomernotmerged.json', 'w', encoding="utf-8") as json_file:
	json.dump(newcomer, json_file, ensure_ascii=False, indent=2)
