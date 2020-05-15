#finds PDF download link on euralex.org item page and adds it to rdf uri
import requests
import csv
import re
from collections import OrderedDict
import json
import os
import urllib3
#import pandas as pd


#get zotero rdf urilist csv

with open('D:/EuralexMerge/Euralex-uri-pdflink.csv', encoding="utf-8") as urifile:
	reader = csv.reader(urifile, delimiter="\t")
	uridict = OrderedDict((rows[1],rows[0]) for rows in reader)
print(uridict)

with open("D:/EuralexMerge/Euralex-extra-categories.json", encoding="utf-8") as f:
	extradata =  json.load(f, encoding="utf-8")
	#extrastr = json.loads(extradata)


#print(extradata)

for pdfurl in uridict:
	#path = urllib3.unquote(path)
	file = os.path.splitext(os.path.basename(pdfurl))[0]
	uri = uridict.get(pdfurl)
	#print("\n"+pdfurl+" IST "+uri)
	for extraitem in extradata:
		if file in str(extraitem):
			print('\nfound match: '+uri.rstrip())
			extraitem['AN'] = uri.rstrip()

with open('D:/EuralexMerge/result.json', 'w') as json_file:
	json.dump(extradata, json_file, indent=2)

#result = OrderedDict()
#for d in (uridict, extradict):
#	for key, value in d.iteritems():
#		result.setdefault(key, []).extend(value)
#print(result)
