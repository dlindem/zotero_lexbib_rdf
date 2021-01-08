import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import csv
import re
import sys

ignore_object_uri = [ # object uri to ignore for import in wikibase
"http://www.w3.org/2002/07/owl#NamedIndividual",
"http://www.w3.org/2002/07/owl#Class",
"http://www.w3.org/2002/07/owl#Thing",
"http://lexbib.org/lexdo/LexdoRootClass"
]

label_properties = { # rdfs and skos labels to QS v1 mapping
"http://www.w3.org/2000/01/rdf-schema#Label":"Len",
"http://www.w3.org/2004/02/skos/core#prefLabel":"Len",
"http://www.w3.org/2004/02/skos/core#altLabel":"Aen"

}

with open('D:/LexBib/wikibase/lwd_labels.json', encoding="utf-8") as f:
	labels =  json.load(f)

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
with open(sparql_csv, 'r', encoding="utf-8") as csvfile:
    csvdict = csv.DictReader(csvfile)
    qscsv = ""
    created = []
    for triple in csvdict:
        #print (str(len(created)))
        if triple['s'] not in ill.values() and triple['s'] not in created: # look for rdf items without Qid
            #print('did not find '+triple['s'])
            qscsv += "CREATE\nLAST\tP3\t\""+triple['s']+"\"\n"
            created.append(triple['s'])
        elif triple['s'] in ill.values():
            print('did find '+triple['s']+', will not propose to create new wikibase item')

if len(created) > 0:
    with open('D:/LexBib/wikibase/qsv1_create_commands.txt', 'w', encoding='utf-8') as qsfile:
        qsfile.write(qscsv)

    print('\nFound new Items. These have to be created first in LWB. Quickstatements V1 item creation commands file written. Finished.\n')
    sys.exit()

print('\nDid not find any new items. Will not write QS item creation file.\nWill proceed looking at properties and objects...\n')


with open(sparql_csv, 'r', encoding="utf-8") as csvfile:
    csvdict = csv.DictReader(csvfile)
    newst = []

    for triple in csvdict:
        #print(triple)
        if triple['s'] in ill.values() and triple['o'] not in ignore_object_uri:
            subject = get_key(ill, triple['s']).replace("http://lexbib.wiki.opencura.com/entity/", "") # replaces with wikibase item Qid
            print('Found known subject '+subject)
            if triple['p'] in pll.values(): # checks in property is known in wikibase
                property = get_key(pll, triple['p']).replace("http://lexbib.wiki.opencura.com/entity/", "") # replaces with wikibase property
                #qscsv += subject+"\t"+property+"\t"
                print('Found known property '+property)
                if re.match(r'https?://', triple['o']): # object is URL or URL
                    if triple['o'] in ill.values(): # if object is a known wikibase item...
                        object = get_key(ill, triple['o']).replace("http://lexbib.wiki.opencura.com/entity/", "") # replace with its Qid
                        newst.append({'subjectqid':subject,'property':property,'object':{'type':'qid','value':object}})
                    else:
                        object = triple['o']
                        newst.append({'subjectqid':subject,'property':property,'object':{'type':'literal','value':object}})
                else:
                    object = triple['o']
                    newst.append({'subjectqid':subject,'property':property,'object':{'type':'literal','value':object}})
            elif triple['p'] in label_properties:

                property = label_properties[triple['p']]
                if subject not in labels:
                	labels[subject]={property:{"value":triple['o']}}
                else:
                	if property not in labels[subject]:
                		labels[subject][property] = {"value":triple['o']}
            else:
                print('\nFound property '+triple['p']+', unknown in lexbib wikibase.')

with open('D:/LexBib/wikibase/lwd_labels.json', 'w', encoding="utf-8") as json_file:
	json.dump(labels, json_file, ensure_ascii=False, indent=2)
print("\nLexBib Wikibase Item Labels json updated.")


with open('D:/LexBib/wikibase/new_statements.json', 'w', encoding="utf-8") as json_file:
	json.dump(newst, json_file, ensure_ascii=False, indent=2)

print('\nLexBib Wikibase new statements json file written. Finished.\n')
