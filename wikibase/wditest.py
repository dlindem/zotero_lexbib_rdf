
from wikidataintegrator import wdi_core, wdi_login

# This is an attempt to write a statement with datatype Time to data.lexbib.org wikibase instance

lwbuser = "DavidL"
with open('D:/LexBib/wikibase/data_lexbib_org_pwd.txt', 'r', encoding='utf-8') as pwdfile:
	lwbpass = pwdfile.read()
mediawiki_api_url = "https://data.lexbib.org/w/api.php" # <- change to applicable wikibase
sparql_endpoint_url = "https://data.lexbib.org/query/sparql"  # <- change to applicable wikibase
login = wdi_login.WDLogin(lwbuser, lwbpass, mediawiki_api_url=mediawiki_api_url)
print(login)

# This does not have any effect:
# wdi_core.config['PROPERTY_CONSTRAINT_PID'] = "P7"
# wdi_core.config['DISTINCT_VALUES_CONSTRAINT_QID'] = "Q16512"
# print(str(wdi_core.config))

wikibaseEntityEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)
print(wikibaseEntityEngine)

lwbqid = "Q307"
lwbprop = "P15"
value = '+2001-12-31T12:01:13Z'

data = []
data.append(wdi_core.WDTime(value, prop_nr=lwbprop))
data.append(wdi_core.WDItemID(value=lwbqid, prop_nr=lwbprop))
print(str(data))

item = wikibaseEntityEngine(data=data)

print(item.write(login))

# If you change this line:
#
# propertiesSparql = wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe=True)
#
# to
#
# propertiesSparql = wdi_core.WDItemEngine.execute_sparql_query(query, mediawiki_api_url=<source wikibase api>, sparql_endpoint_url=<source WDQS>, as_dataframe=True)
#
# you can apply it to replicate a the properties from one wikibase to another
