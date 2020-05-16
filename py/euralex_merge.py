#merges extra csv column to json file (for a special case of data import), by dlindem
import csv
import re
from collections import OrderedDict
import json
import os
import re

#import pandas as pd


#get zotero rdf urilist csv

with open('D:/EuralexMerge/Euralex-uri-pdflink.csv', encoding="utf-8") as urifile:
	reader = csv.reader(urifile, delimiter="\t")
	uridict = OrderedDict((rows[1],rows[0]) for rows in reader)
print(uridict)

with open("D:/EuralexMerge/Euralex-extra-categories.json", encoding="utf-8") as f:
	extradata =  json.load(f, encoding="utf-8")
	#extrastr = json.loads(extradata)


print(extradata)

for item in extradata:
	for key in item:
		item[key] = [item[key]]

for pdfurl in uridict:
	#path = urllib3.unquote(path)
	file = re.sub('[^A-Za-z0-9]','',os.path.splitext(os.path.basename(pdfurl))[0])
	uri = uridict.get(pdfurl)
	#print("\n"+file+" IST "+uri)
	for extraitem in extradata:
		teststr = re.sub('[^A-Za-z0-9]','',str(extraitem))
		#print(teststr)
		if file in teststr:
			print('\nfound match: '+uri.rstrip())
			extraitem['AN'] = [uri.rstrip()]

with open('D:/EuralexMerge/result.json', 'w', encoding="utf-8") as json_file:
	json.dump(extradata, json_file, ensure_ascii=False, indent=2)

#result = OrderedDict()
#for d in (uridict, extradict):
#	for key, value in d.iteritems():
#		result.setdefault(key, []).extend(value)
#print(result)
