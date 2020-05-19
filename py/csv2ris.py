# converts CSV into JSON (keys in first csv row), by dlindem
import re
import json
import csv

with open('D:/LexikosMerge/Elexifinder-Lexikos-extrafields.csv', encoding="utf-8") as csvfile:
    csvdict = csv.DictReader(csvfile, delimiter="\t")
    csvjson = []
    for itemdict in csvdict:
        for riskey in itemdict:
            itemdict[riskey] = [itemdict[riskey]]
        csvjson.append(itemdict)
print(csvjson)

with open('D:/LexikosMerge/csv2json.json', 'w', encoding="utf-8") as json_file:
	json.dump(csvjson, json_file, ensure_ascii=False, indent=2)
