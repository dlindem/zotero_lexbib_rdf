from SPARQLWrapper import SPARQLWrapper, JSON
import json
import time
import mwclient

with open('D:/LexBib/places/places_wdplaces.json', encoding="utf-8") as f:
	places =  json.load(f)

#setup wikidata query premises
sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='LexBib-Bibliodata-enrichment-script (lexbib.org)')

#setup lwb writing premises
with open('D:/LexBib/wikibase/pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()
lwb = mwclient.Site('lexbib.wiki.opencura.com')
login = lwb.login(username='DavidL', password=pwd)
#print(login)
csrfquery = lwb.api('query', meta='tokens')
#print (str(csrfquery))
token=csrfquery['query']['tokens']['csrftoken']

#process places
for place in places:
    wdqid = place['wdplace'].replace("http://www.wikidata.org/entity/","")
    print (wdqid)
    #query wikidata

    sparql.setQuery("SELECT ?longitude ?latitude WHERE {wd:"+wdqid+" p:P625 [psv:P625 [wikibase:geoLongitude ?longitude;wikibase:geoLatitude ?latitude]] .} limit 50")
    sparql.setReturnFormat(JSON)
    #wdquerycount = wdquerycount + 1
    try:
        time.sleep(1)
        wddict = sparql.query().convert()
        #print (wddict['results']['bindings'])
        longitude = wddict['results']['bindings'][0]['longitude']['value']
        latitude = wddict['results']['bindings'][0]['latitude']['value']
        print(longitude+' | '+latitude)
    except Exception as ex:
        print("error at processing place: "+place['place']+": "+str(ex))

    # insert here check if coordinates are already in LWB for this place
    lwbqid = place['place'].replace('http://lexbib.wiki.opencura.com/entity/','')
    prop="P23"

    results = lwb.post('wbcreateclaim', token=token, entity=lwbqid, property=prop, snaktype="value", value='{"latitude":'+latitude+',"longitude":'+longitude+', "precision":0.000001}')
    if results['success'] == 1:
    	print('Wbsetclaim for '+lwbqid+' ('+prop+') '+latitude+'|'+longitude+': success.')
    else:
    	print('Wbsetclaim for '+lwbqid+' ('+prop+') '+latitude+'|'+longitude+': ERROR.')
