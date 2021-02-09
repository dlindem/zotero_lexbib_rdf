from SPARQLWrapper import SPARQLWrapper, JSON
import json
import sys

sparql = SPARQLWrapper("https://lexbib.wiki.opencura.com/query/sparql", agent='LexBib (lexbib.org)')

# # LWB - LexDo Properties mappings (SPARQL query for unknown reasons does not work from inside the script...)
# with open('propmapping.rq', 'r') as file:
#     propmapping = file.read()
#     print(propmapping)
#
# propmapping = 'SELECT DISTINCT ?lwbProp ?lwbPropName ?valueconstraint ?type ?lexdoProp    WHERE    { ?lwbProp rdf:type <http://wikiba.se/ontology#Property> .  OPTIONAL {?lwbProp rdfs:label ?lwbPropName .          }  OPTIONAL{  ?lwbProp <http://wikiba.se/ontology#propertyType> ?type.          }  OPTIONAL{?lwbProp <http://lexbib.wiki.opencura.com/prop/direct/P1> ?lexdoProp .          }  OPTIONAL{?lwbProp <http://lexbib.wiki.opencura.com/prop/direct/P42>  ?valueconstraint .          }  }  '
#
# sparql.setQuery(propmapping)
# sparql.setReturnFormat(JSON)
#
# try:
#     #time.sleep(1.5)
#     sparqldict = sparql.query().convert()
#     datalist = sparqldict['results']['bindings']
#     print(datalist)
# except Exception as ex:
#     print(str(ex))
#     pass
#
# with open('D:/LexBib/wikibase/properties_lwb_lexdo.json', 'w', encoding="utf-8") as json_file:
# 	json.dump(datalist, json_file, ensure_ascii=False, indent=2)
# print("\nLexBib Wikibase Properties and LexDo RDF properties mapping json updated.\n")
#
# sys.exit()

# LWB - Wikidata Properties mappings

# sparql.setQuery('SELECT ?lwbProp ?lwbPropName ?wdProp  WHERE {  ?lwbProp ?directClaimP ?wdProp . ?p wikibase:directClaim ?directClaimP . FILTER (STRENDS(str(?p), "P2")) OPTIONAL{?lwbProp rdfs:label ?lwbPropName .} }')
# sparql.setReturnFormat(JSON)
#
# try:
#     #time.sleep(1.5)
#     sparqldict = sparql.query().convert()
#     datalist = sparqldict['results']['bindings']
#     #print(datalist)
# except Exception as ex:
#     print(str(ex))
#     pass
#
# with open('D:/LexBib/wikibase/properties_lwb_wikidata.json', 'w', encoding="utf-8") as json_file:
# 	json.dump(datalist, json_file, ensure_ascii=False, indent=2)
# print("\nLexBib Wikibase Properties and Wikidata properties mapping json updated.\n")

# LWB - LexDo RDF Items mappings
print("Updating LexBib Wikibase Items and LexDo RDF Items mapping...")
sparql.setQuery('SELECT ?lwbItem ?lwbItemName ?lexdoItem  WHERE {  ?lwbItem ?directClaimP ?lexdoItem . ?p wikibase:directClaim ?directClaimP . FILTER (STRENDS(str(?p), "P3")) OPTIONAL{?lwbItem rdfs:label ?lwbItemName .} }')
sparql.setReturnFormat(JSON)

try:
    #time.sleep(1.5)
    sparqldict = sparql.query().convert()
    datalist = sparqldict['results']['bindings']
    #print(datalist)
except Exception as ex:
    #print(str(ex))
    pass

with open('D:/LexBib/wikibase/items_lwb_lexdo.json', 'w', encoding="utf-8") as json_file:
	json.dump(datalist, json_file, ensure_ascii=False, indent=2)
print("\nLexBib Wikibase Items and LexDo RDF Items mapping json updated.\n")

# LWB - Wikidata Items mappings
print("Updating LexBib Wikibase Items and Wikidata Items mapping...")

sparql.setQuery('SELECT ?lwbItem ?lwbItemName ?wdItem  WHERE {  ?lwbItem ?directClaimP ?wdItem . ?p wikibase:directClaim ?directClaimP . FILTER (STRENDS(str(?p), "P4")) OPTIONAL{?lwbItem rdfs:label ?lwbItemName .} }')
sparql.setReturnFormat(JSON)

try:
    #time.sleep(1.5)
    sparqldict = sparql.query().convert()
    datalist = sparqldict['results']['bindings']
    #print(datalist)
except Exception as ex:
    print(str(ex))
    pass

with open('D:/LexBib/wikibase/items_lwb_wikidata.json', 'w', encoding="utf-8") as json_file:
	json.dump(datalist, json_file, ensure_ascii=False, indent=2)
print("\nLexBib Wikibase Items and Wikidata Items mapping json updated. Finished.\n")
