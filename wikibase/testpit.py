#import lwb
from wikidataintegrator import wdi_core, wdi_login

mediawiki_api_url = "https://data.lexbib.org/w/api.php" # <- change to applicable wikibase
sparql_endpoint_url = "https://data.lexbib.org/query/sparql"  # <- change to applicable wikibase


claim = wdi_core.WDItemEngine(wd_item_id="Q16492", mediawiki_api_url=mediawiki_api_url).get_label(lang="en")
print(str(claim))
