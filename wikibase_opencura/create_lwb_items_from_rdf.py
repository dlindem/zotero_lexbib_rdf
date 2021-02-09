import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import csv

def get_key(dict, val):
    for key, value in dict.items():
         if val == value:
             return key

#if "http://lexbib.org/lexdo/" in ill.values():
#    print('found key '+get_key(ill, "http://lexbib.org/lexdo/"))

with open('D:/LexBib/wikibase/properties_lwb_lexdo.json', encoding="utf-8") as f:
	properties_lwb_lexdo =  json.load(f, encoding="utf-8")
pll = {}
for item in properties_lwb_lexdo:
    pll[item['lwbProp']['value']] = item['lexdoProp']['value']

with open('D:/LexBib/wikibase/properties_lwb_wikidata.json', encoding="utf-8") as f:
	properties_lwb_wikidata =  json.load(f, encoding="utf-8")
plw = {}
for item in properties_lwb_wikidata:
    plw[item['lwbProp']['value']] = item['wdProp']['value']

with open('D:/LexBib/wikibase/items_lwb_lexdo.json', encoding="utf-8") as f:
	items_lwb_lexdo =  json.load(f, encoding="utf-8")
ill = {}
for item in items_lwb_lexdo:
    ill[item['lwbItem']['value']] = item['lexdoItem']['value']

with open('D:/LexBib/wikibase/items_lwb_wikidata.json', encoding="utf-8") as f:
	items_lwb_wikidata =  json.load(f, encoding="utf-8")
ilw = {}
for item in items_lwb_wikidata:
    ilw[item['lwbItem']['value']] = item['wdItem']['value']

print ('\nMapping JSON files loaded.\n')

Tk().withdraw()
sparql_csv = askopenfilename()
print('File to process is '+sparql_csv)
csvdict = csv.DictReader(open(sparql_csv))
qscsv = ""
created = []
for triple in csvdict:
    #print (str(len(created)))
    if triple['s'] not in ill.values() and triple['s'] not in created:
        #print('did not find '+triple['s'])
        qscsv += "CREATE\nLAST\tP3\t\""+triple['s']+"\"\n"
        created.append(triple['s'])
    elif triple['s'] in ill.values():
        print('did find '+triple['s']+', will not propose to create new wikibase item')

if len(created) == 0:
    print('\nDid not find any new items. Will not write QS csv file. Finished.\n')
else:

    with open('D:/LexBib/wikibase/qsv1commands.txt', 'w', encoding='utf-8') as qsfile:
        qsfile.write(qscsv)

    print('\nQuickstatements V1 commands file written. Finished.\n')
