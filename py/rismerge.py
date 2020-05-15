# joins two RIS-JSON files, common pivot key "AN", by dlindem
import json

with open("D:/EuralexMerge/convertedris.json", encoding="utf-8") as f:
	original =  json.load(f, encoding="utf-8")
with open("D:/EuralexMerge/result.json", encoding="utf-8") as f:
	newcomer =  json.load(f, encoding="utf-8")

for origitem in original:
	#print(origitem)
	#print(origitem['AN'])
	for newitem in newcomer:
		if 'AN' in newitem and 'AN' in origitem and str(origitem['AN']) == str(newitem['AN']):
			print('found merge candidate')
			for key, value in origitem.items():
				try:
					origitem[key].extend(newitem[key])
				except KeyError:
					pass
			for key, value in newitem.items():
				if origitem.get(key) == None:
					origitem[key] = newitem[key]



with open('D:/EuralexMerge/mergedris.json', 'w', encoding="utf-8") as json_file:
	json.dump(original, json_file, ensure_ascii=False, indent=2)
