import mwclient
import time
import json
from SPARQLWrapper import SPARQLWrapper, JSON


sparql = SPARQLWrapper("https://lexbib.wiki.opencura.com/query/sparql", agent='LexBib (lexbib.org)')

# LWB - LexDo Properties mappings

sparql.setQuery('select ?lexdo_p ?lwb_p ?type where {?lwb_p rdf:type <http://wikiba.se/ontology#Property>. ?lwb_p <http://wikiba.se/ontology#propertyType> ?type. ?lwb_p <http://lexbib.wiki.opencura.com/prop/direct/P1> ?lexdo_p.}')
sparql.setReturnFormat(JSON)

try:
    #time.sleep(1.5)
    sparqldict = sparql.query().convert()
	propdict = {}
    for prop in sparqldict['results']['bindings']:
		propdict[prop['lexdo_p']['value']] = {lwb_p:[prop]['lwb_p']['value'], type:[prop]['type']['value']}
    print(propdict)
except Exception as ex:
    print(str(ex))
    pass


# LexBib wikibase OAuth
site = mwclient.Site('lexbib.wiki.opencura.com')
with open('D:/LexBib/wikibase/pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()
def get_token():
	login = site.login(username='DavidL', password=pwd)
	csrfquery = site.api('query', meta='tokens')
	token=csrfquery['query']['tokens']['csrftoken']
	return token

# get rdf2lwb_api.py output
with open('D:/LexBib/wikibase/new_statements.json', encoding="utf-8") as f:
	triples =  json.load(f)

# process triples
token = get_token()
with open('errorlog_'+time.strftime("%Y%m%d-%H%M%S")+'.log', 'w') as errorlog:
	for triple in triples:

		qid = triple['subjectqid']
		prop = triple['property']
		try:
			if triple['object']['type'] == "literal":
				if prop == "P29" or prop == "P28": #dct:date, TODO, container: TODO
					results = None
					#object='"+'+triple['object']['value']+'"'
					#results = site.post('wbcreateclaim', token=token, entity=qid, property=prop, snaktype="value", value='{"timezone":0,"precision":9,"before":0,"after":0,"time":"+2006-01-01T02:00:00.000Z"}')
				else:

					object = '"'+triple['object']['value']+'"'
					#print('Triple: '+qid+' ('+prop+') '+object)
					#results = site.api('wbeditentity', token=token, id=qid, data={"claims":[{"mainsnak":{"snaktype":"value","property":prop,"datavalue":{"value":object,"type":"string"}},"type":"statement","rank":"normal"}]})
					results = site.post('wbcreateclaim', token=token, entity=qid, property=prop, snaktype="value", value=object)
			elif triple['object']['type'] == "qid":
				object = triple['object']['value']
				results = site.post('wbcreateclaim', token=token, entity=qid, property=prop, snaktype="value", value='{"entity-type":"item","numeric-id":'+object.replace("Q","")+'}')
			if results != None and results['success'] == 1:
				print('Wbsetclaim for '+qid+' ('+prop+') '+object+': success.')
			elif results = None:
				print('Wbsetclaim for '+qid+' ('+prop+'): *** Hardcoded SKIP.')
			else:
				print('Wbsetclaim for '+qid+' ('+prop+'): *** Unknown error not raised to exception.')
		except Exception as ex:
			print(str(ex))
			if 'Invalid CSRF token.' in ex:
				token = get_token()
			errorlog.write('\n\nError at QID (prop): \n'+qid+' ('+prop+')\n'+str(ex))
