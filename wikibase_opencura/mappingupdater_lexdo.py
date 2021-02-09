from rdflib import Graph, Namespace, BNode, URIRef, Literal
import json

with open('D:/LexBib/wikibase/items_lwb_lexdo.json', encoding="utf-8") as f:
	items_lwb_lexdo =  json.load(f, encoding="utf-8")
with open('D:/LexBib/wikibase/items_lwb_wikidata.json', encoding="utf-8") as f:
	items_lwb_wikidata =  json.load(f, encoding="utf-8")
ilw = {}
for item in items_lwb_wikidata:
    ilw[item['lwbItem']['value']] = item['wdItem']['value']

mapg = Graph()

wd = Namespace ('http://www.wikidata.org/entity/')
lexdo = Namespace('http://lexbib.org/lexdo/')
lwb = Namespace ('http://lexbib.wiki.opencura.com/entity/')
mapg.bind("wd", wd)
mapg.bind("lexdo", lexdo)
mapg.bind("lwb", lwb)

lwbcount = 0
wdcount = 0
for item in items_lwb_lexdo:
    lexdoitem = URIRef(item['lexdoItem']['value'])
    lwbitem = URIRef(item['lwbItem']['value'])
    mapg.add((lexdoitem, lexdo.lwbItem, lwbitem))
    lwbcount +=1
    if item['lwbItem']['value'] in ilw:
        wditem = URIRef(ilw[item['lwbItem']['value']])
        wdqid = Literal(ilw[item['lwbItem']['value']].replace("http://www.wikidata.org/entity/",""))
        mapg.add((lexdoitem, lexdo.wdItem, wditem))
        mapg.add((lexdoitem, lexdo.wdQid, wdqid))
        wdcount += 1

mapg.serialize(destination='D:/LexBib/wikibase/lwb_lexdo_mapping.ttl', format="turtle")

print('Finished. Processed '+str(lwbcount)+' Lexdo-to-LWB mappings, and '+str(wdcount)+' Lexdo-to-WD mappings.')
