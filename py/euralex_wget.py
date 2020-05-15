#finds PDF download link on euralex.org item page and adds it to rdf uri
import requests
import csv
import re


#get zotero rdf urilist csv

risfile = open('D:/EuralexMerge/euralex-rdf-uri.csv', 'r')
rdfurilines = rdfurifile.readlines()

with open('D:/EuralexMerge/mergeresult.csv', mode='w') as resultfile:
	#result_writer = csv.writer(resultfile, delimiter=',')
	count = 1
	for url in rdfurilines:
		r = requests.get(url)
		page_source = r.text
		match = re.search('<td>Download</td><td><a href="([^"]+)">', page_source)
		resultline = url.rstrip()+"\t"+match.group(1)+"\n"
		resultfile.write(resultline)
		print('count '+str(count)+": "+resultline)
		count = count + 1
