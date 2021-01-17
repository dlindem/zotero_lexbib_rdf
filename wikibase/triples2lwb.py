import mwclient
import time
import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import csv
import re
import traceback

# get key function
def get_key(dict, val):
	for key, value in dict.items():
		if val == value:
			return key

# class entities to ignore for import of rdf:type in wikibase
ignore_classes = [
"http://www.w3.org/2002/07/owl#NamedIndividual",
"http://www.w3.org/2002/07/owl#Class",
"http://www.w3.org/2002/07/owl#Thing",
"http://purl.org/ontology/bibo/Document",
"http://purl.org/ontology/bibo/document",
"http://purl.org/ontology/bibo/Article",
"http://lexbib.org/lexdo/BibliographicalResource",
"http://lexbib.org/lexdo-top/Resource",
"http://xmlns.com/foaf/0.1/Document",
"http://purl.org/ontology/bibo/Proceedings",
"http://purl.org/ontology/bibo/Collection"
]

# label properties
label_properties = { # rdfs and skos labels to QS v1 mapping
"http://www.w3.org/2000/01/rdf-schema#label":"Len",
"http://www.w3.org/2004/02/skos/core#prefLabel":"Len",
"http://www.w3.org/2004/02/skos/core#altLabel":"Aen"
}


# get item uri mappings
with open('D:/LexBib/wikibase/items_lwb_lexdo.json', encoding="utf-8") as f:
	items_lwb_lexdo =json.load(f)
ill = {}
for item in items_lwb_lexdo:
	ill[item['lwbItem']['value']] = item['lexdoItem']['value'].rstrip("/")

with open('D:/LexBib/wikibase/items_lwb_wikidata.json', encoding="utf-8") as f:
	items_lwb_wikidata =json.load(f)
ilw = {}
for item in items_lwb_wikidata:
	ilw[item['lwbItem']['value']] = item['wdItem']['value']

print ('\nMapping JSON files loaded.\n')

#get CSV file to import, first row must be: '?s,?p,?o\n'
Tk().withdraw()
sparql_csv = askopenfilename()
print('File to process is '+sparql_csv)

print('\nDo you want to find new subjects and create them in lwb?\nYes = 1, No = 0 \n')
try:
	choice = int(input())
	print ('Your choice: '+str(choice)+', will start to process...')
except:
	print ('Error: This has to be a number.')
	sys.exit()

if choice == 1:
	with open(sparql_csv, 'r', encoding="utf-8") as csvfile:
		csvdict = csv.DictReader(csvfile)
		qscsv = ""
		created = []
		seen = ""
		for triple in csvdict:
			#print (str(len(created)))
			if triple['s'] not in ill.values() and triple['s'] not in created: # look for rdf items without Qid
				#print('did not find '+triple['s'])
				qscsv += "CREATE\nLAST\tP3\t\""+triple['s']+"\"\n"
				created.append(triple['s'])
				print('*** Found new item (appended to create command list): '+triple['s'])
			elif triple['s'] in ill.values():
				if triple['s'] != seen:
					print('Found '+triple['s']+', will not propose to create new wikibase item')
					seen = triple['s']
	if len(created) > 0:
		with open('D:/LexBib/wikibase/qsv1_create_commands.txt', 'w', encoding='utf-8') as qsfile:
			qsfile.write(qscsv)

		print('\nFound new subjects. These have to be created first in LWB. Quickstatements V1 item creation commands file written. Finished.\n')
	else:
		print('\nDid not find any new subjects. Finished.')
	sys.exit() # script stops if there have been unknown items

# process new statements

with open('D:/LexBib/wikibase/properties_lwb_lexdo_type.json', encoding="utf-8") as f:
	data =  json.load(f)['results']['bindings']
	propdict = {}
	for prop in data:
		if 'lexdoProp' in prop:
			propdict[prop['lexdoProp']['value']] = {"lwb_p":prop['lwbProp']['value'], "type":prop['type']['value']}
			if "valueconstraint" in prop:
				propdict[prop['lexdoProp']['value']]['valueconstraint'] = prop['valueconstraint']['value']

	#print(propdict)


# LexBib wikibase OAuth
site = mwclient.Site('lexbib.wiki.opencura.com')
with open('D:/LexBib/wikibase/pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()
def get_token():
	print('Getting fresh login token...')
	login = site.login(username='DavidL', password=pwd)
	csrfquery = site.api('query', meta='tokens')
	token=csrfquery['query']['tokens']['csrftoken']
	return token
token = get_token() # get first new token
with open(sparql_csv, 'r', encoding="utf-8") as csvfile:
	rows = csv.DictReader(csvfile)
	totalrows = 0
	triples = []
	for row in rows:
		triples.append(row)
		totalrows += 1
	print('This will be '+str(totalrows)+' rows to process.')

	with open('D:/LexBib/wikibase/logs/errorlog_'+time.strftime("%Y%m%d-%H%M%S")+'.log', 'w') as errorlog:
		index = 0
		edits = 0
		rep = 0
		while index < totalrows:
			if rep > 5:
				print ('\n...this script has entered in an endless loop... Abort.')
				sys.exit()
			print('Finished processing line '+str(index)+'. '+str(totalrows-index)+' lines left.')
			#time.sleep(1)
			rep += 1
			try:
				triple = triples[index]
				print('\nLine '+str(index+1)+': Triple to process will be: '+str(triple))
				vmax = 0
				if triple['s'] in ill.values() and triple['o'] not in ignore_classes:
					qid = get_key(ill, triple['s']).replace("http://lexbib.wiki.opencura.com/entity/", "") # replaces with wikibase item Qid
					print('Found known subject '+qid+'.')
					if triple['p'] in label_properties: # checks if property is known label property
						print('Found label property '+triple['p'])
						label = label_properties[triple['p']]
						language = re.sub(r'^L|A','',label)
						value = triple['o'].replace('"', '\\"').replace("'", '\\"')[0:250]
						if label[0] == "L":
							results = site.post('wbsetlabel', id=qid, language=language, value=value, token=token)
						elif label[0] == "A":
							results = site.post('wbsetaliases', id=qid, language=language, add=value, token=token)
						for result in results:
							if "success" in result:
								print('Wbsetlabel/alias (Type '+label[0]+') for '+qid+' ('+value+'):'+result)
								#labels[qid][label]['update'] = str(datetime.now())
								index += 1
								rep = 0
					elif triple['p'] in propdict: # checks in property is known in wikibase
						print('Found known property '+triple['p']+'.')
						proptype = propdict[triple['p']]['type'].replace("http://wikiba.se/ontology#", "") # replaces with wikibase property datatype
						print('Found proptype '+proptype+'.')
						property = propdict[triple['p']]['lwb_p'].replace("http://lexbib.wiki.opencura.com/entity/", "") # replaces with wikibase property Pid
						print('Property will be '+property+'.')
						if 'valueconstraint' in propdict[triple['p']]:
							if 'MAX 1' in propdict[triple['p']]['valueconstraint']:
								vmax = 1
							else:
								vmax = 0
						if proptype == "WikibaseItem":

							if triple['o'].rstrip("/") in ill.values(): # if object is a known wikibase item...

								object = get_key(ill, triple['o'].rstrip("/")).replace("http://lexbib.wiki.opencura.com/entity/", "") # replace with its Qid
								print('Found known QID '+object+' for object.')

								results = site.api('wbgetclaims', entity=qid, property=property)
								#print(str(results))
								redundant = 0
								foundobj = None
								if 'claims' in results and property in results['claims']:
									for result in results['claims'][property]:
										foundobj = result['mainsnak']['datavalue']['value']['id']
										guid = result['id']
										##print(foundobj+', GUID '+guid)
										if object == foundobj:
											redundant += 1
											print('Found redundant Object: '+object+'. Will not write new statement.')
											if redundant == 2:
												# todo: delete accidentally created redundancies
												results = site.post('wbremoveclaims', claim=guid, token=token)
												if results['success'] == 1:
													print('Wb remove duplicate claim for '+qid+' ('+property+') '+object+': success.')
													edits += 1
													time.sleep(1)
													redundant = 1
												else:
													print('*** *** Wb remove duplicate claim for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
													errorlog.write('*** Wb remove duplicate claim Error at input line '+str(index)+' for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
								if redundant == 0:
									numqidobject = object.replace("Q", "") # replace with its Qid numeric
									if foundobj == None or vmax == 0:
										results = site.post('wbcreateclaim', token=token, entity=qid, property=property, snaktype="value", value='{"entity-type":"item","numeric-id":'+numqidobject+'}')
										if results['success'] == 1:
											print('Wb create claim for '+qid+' ('+property+') '+object+': success.')
											edits += 1
											time.sleep(1)
										else:
											print('*** *** Wbcreateclaim for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
											errorlog.write('*** Wbcreateclaim Error at input line '+str(index)+' for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
									elif vmax == 1:
										results = site.post('wbsetclaimvalue', token=token, claim=guid, snaktype="value", value='{"entity-type":"item","numeric-id":'+numqidobject+'}')
										if results['success'] == 1:
											edits += 1
											time.sleep(1)
											print('Wb update claim value for '+qid+' ('+property+') '+object+': success.')
										else:
											print('*** *** Wb update claim value for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
											errorlog.write('\n*** Wb update claim Error at input line '+str(index)+' for '+qid+' ('+property+'): *** Unknown error not raised to exception.')

								index += 1
								rep = 0
							else:
								print('Error: '+triple['o']+' was supposed to correspond to an LWB item but it is not.')
								errorlog.write('\n\nError at line '+str(index)+', '+qid+' ('+property+'): '+triple['o']+' (was supposed to be an LWB item but it is not).')
								index += 1
								rep = 0

						elif proptype == "Time":
							property = "P45" # workaround until real implementation of datatype time (P45 takes string)
							object = '"'+triple['o'][0:4]+'"'
							results = site.api('wbgetclaims', entity=qid, property=property)
							#print('Wbgetclaims:\n'+str(results['claims']))
							redundant = 0
							foundobj = None
							if 'claims' in results and property in results['claims']:
								for result in results['claims'][property]:
									foundobj = result['mainsnak']['datavalue']['value']
									guid = result['id']
									#print(str(foundobj)+', GUID '+str(guid))
									if triple['o'] == foundobj:
										redundant += 1
										print('Found redundant Object: '+object+'. Will not write new statement.')
										if redundant == 2:
											# todo: delete accidentally created redundancies
											results = site.post('wbremoveclaims', claim=guid, token=token)
											if results['success'] == 1:
												print('Wb remove duplicate claim for '+qid+' ('+property+') '+object+': success.')
												edits += 1
												time.sleep(1)
												redundant = 1
											else:
												print('*** *** Wb remove duplicate claim for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
												errorlog.write('*** Wb remove duplicate claim Error at input line '+str(index)+' for '+qid+' ('+property+'): *** Unknown error not raised to exception.')

							if redundant == 0:
								if foundobj == None or vmax == 0:
									results = site.post('wbcreateclaim', token=token, entity=qid, property=property, snaktype="value", value=object)
									if results['success'] == 1:
										edits += 1
										time.sleep(1)
										print('Wbcreateclaim for '+qid+' ('+property+') '+object+': success.')
									else:
										print('*** *** Wbcreateclaim for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
										errorlog.write('*** Wbcreateclaim Error at input line '+str(index)+' for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
								elif vmax == 1:
									results = site.post('wbsetclaimvalue', token=token, claim=guid, snaktype="value", value=object)
									if results['success'] == 1:
										edits += 1
										time.sleep(1)
										print('wbsetclaimvalue for '+qid+' ('+property+')'+guid+' > '+object+': success.')
									else:
										print('*** *** Wb update claim value for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
										errorlog.write('\n*** Wb update claim Error at input line '+str(index)+' for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
							index += 1
							rep = 0


						elif proptype == "ExternalId" or proptype == "String" or proptype == "Url":
							object = '"'+triple['o'].replace('"', '\\"').replace("'", '\\"')+'"'
							results = site.api('wbgetclaims', entity=qid, property=property)
							#print('Wbgetclaims:\n'+str(results['claims']))
							redundant = 0
							foundobj = None
							if 'claims' in results and property in results['claims']:
								for result in results['claims'][property]:
									foundobj = result['mainsnak']['datavalue']['value']
									guid = result['id']
									#print(str(foundobj)+', GUID '+str(guid))
									if triple['o'] == foundobj:
										redundant += 1
										print('Found redundant Object: '+object+'. Will not write new statement.')
										if redundant == 2:
											# todo: delete accidentally created redundancies
											results = site.post('wbremoveclaims', claim=guid, token=token)
											if results['success'] == 1:
												print('Wb remove duplicate claim for '+qid+' ('+property+') '+object+': success.')
												edits += 1
												time.sleep(1)
												redundant = 1
											else:
												print('*** *** Wb remove duplicate claim for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
												errorlog.write('*** Wb remove duplicate claim Error at input line '+str(index)+' for '+qid+' ('+property+'): *** Unknown error not raised to exception.')

							if redundant == 0:
								if foundobj == None or vmax == 0:
									results = site.post('wbcreateclaim', token=token, entity=qid, property=property, snaktype="value", value=object)
									if results['success'] == 1:
										edits += 1
										time.sleep(1)
										print('Wbcreateclaim for '+qid+' ('+property+') '+object+': success.')
									else:
										print('*** *** Wbcreateclaim for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
										errorlog.write('*** Wbcreateclaim Error at input line '+str(index)+' for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
								elif vmax == 1:
									results = site.post('wbsetclaimvalue', token=token, claim=guid, snaktype="value", value=object)
									if results['success'] == 1:
										edits += 1
										time.sleep(1)
										print('wbsetclaimvalue for '+qid+' ('+property+')'+guid+' > '+object+': success.')
									else:
										print('*** *** Wb update claim value for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
										errorlog.write('\n*** Wb update claim Error at input line '+str(index)+' for '+qid+' ('+property+'): *** Unknown error not raised to exception.')
							index += 1
							rep = 0

						else:
							print('Found datatype \"' +proptype+'\", not implemented yet. Skipped.')
							index += 1
							rep = 0
					else:
						print('Found property '+triple['p']+', unknown in lexbib wikibase. Skipped.')
						index += 1
						rep = 0
				else:
					if triple['s'] not in ill.values() and triple['o'] in ignore_classes:
						print ('There shouldn\'t be unknown subjects. Run this script again in 1 mode.')
						errorlog.write('There shouldn\'t be unknown subjects. Run this script again in 1 mode.')
					elif triple['o'] in ignore_classes:
						print('This rdf:Class is on the ignore list. Skipped.')
					else:
						print('Skipped. Don\'t ask me why.')
					index += 1
					rep = 0
			except Exception as ex:
				traceback.print_exc()
				if 'Invalid CSRF token.' in str(ex):
					print('Wait a sec. Must get a new CSRF token...')
					token = get_token()
				errorlog.write('\n\nError at input line '+str(index)+', qid (prop): '+qid+' ('+property+'): \n'+str(ex))

print ('Finished processing '+str(index)+' lines, '+str(edits)+' edits made.')
