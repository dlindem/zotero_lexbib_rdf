sparql = SPARQLWrapper("https://lexbib.wiki.opencura.com/query/sparql", agent='LexBib (lexbib.org)')

# LWB - LexDo Properties mappings

sparql.setQuery('SELECT ?lexdo_p ?lwb_p ?type WHERE {?lwb_p <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://wikiba.se/ontology#Property>. ?lwb_p <http://wikiba.se/ontology#propertyType> ?type. ?lwb_p <http://lexbib.wiki.opencura.com/prop/direct/P1> ?lexdo_p.}')
sparql.setReturnFormat(JSON)

try:
	#time.sleep(1.5)
	sparqldict = sparql.query().convert()
	print(sparqldict)
	data = sparqldict['results']['bindings']
	propdict = {}
	for prop in data:
		propdict[data[prop]['lexdo_p']['value']] = {lwb_p:data[prop]['lwb_p']['value'], type:data[prop]['type']['value']}
	print(propdict)
except Exception as ex:
	print(str(ex))
	pass
