# This is an attempt to write a statement with datatype Time to data.lexbib.org wikibase instance

from wikidataintegrator import wdi_core, wdi_login

# from wikidataintegrator.wdi_config import config as wdi_config
#
# wdi_config['MEDIAWIKI_API_URL'] = 'https://data.lexbib.org/w/api.php'
# wdi_config['SPARQL_ENDPOINT_URL'] = 'https://data.lexbib.org/query/sparql'
# wdi_config['WIKIBASE_URL'] = 'http://data.lexbib.org'
# wdi_config['PROPERTY_CONSTRAINT_PID'] = 'P7'
# wdi_config['DISTINCT_VALUES_CONSTRAINT_QID'] = 'Q16512'


lwbuser = "DavidL"
with open('D:/LexBib/wikibase/data_lexbib_org_pwd.txt', 'r', encoding='utf-8') as pwdfile:
	lwbpass = pwdfile.read()
mediawiki_api_url = "https://data.lexbib.org/w/api.php" # <- change to applicable wikibase
sparql_endpoint_url = "https://data.lexbib.org/query/sparql"  # <- change to applicable wikibase
login = wdi_login.WDLogin(lwbuser, lwbpass, mediawiki_api_url=mediawiki_api_url)
lwbEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)

lwbqid = "Q307"
lwbprop = "P15"
value = '+2013-01-01T00:00:00Z'

data = []
data.append(wdi_core.WDTime(value, prop_nr=lwbprop))
#data.append(wdi_core.WDItemID(value=lwbqid, prop_nr=lwbprop))
#print(str(data))

item = lwbEngine(wd_item_id=lwbqid, data=data)

print('Success: '+item.write(login))

# If you change this line:
#
# propertiesSparql = wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe=True)
#
# to
#
# propertiesSparql = wdi_core.WDItemEngine.execute_sparql_query(query, mediawiki_api_url=<source wikibase api>, sparql_endpoint_url=<source WDQS>, as_dataframe=True)
#
# you can apply it to replicate a the properties from one wikibase to another
