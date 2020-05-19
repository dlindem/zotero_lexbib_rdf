# finds Wikidata page titles in location property values and replaces them with wikidata uri, by dlindem
import re
import os
import requests
import wget
import json

zotero_lexbib_rdf_export_file = 'D:/LexBib/exports/test.rdf'

with open(zotero_lexbib_rdf_export_file, 'r', encoding="utf-8") as infile:
    exportlines = infile.readlines()

print(exportlines)

with open(os.path.splitext(zotero_lexbib_rdf_export_file)[0]+"_wikidata.rdf", 'w', encoding="utf-8") as outfile:
    for line in exportlines:
        aulocmatch = re.search('([^<]*)<lexdo:firstAuLoc>https?://en.wikipedia.org/wiki/([^<]+)</lexdo:firstAuLoc>', line)
        arlocmatch = re.search('([^<]*)<lexdo:articleLoc>https?://en.wikipedia.org/wiki/([^<]+)</lexdo:articleLoc>', line)
        if aulocmatch != None:
            print(aulocmatch.group(2))
            wdjsonsource = requests.get(url='https://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&format=json&titles='+aulocmatch.group(2))
            wdjson =  wdjsonsource.json()
            entities = wdjson['entities']
            for wdid in entities:
                print(wdid)
                line = aulocmatch.group(1)+'<lexdo:firstAuLoc>http://wikidata.org/entity/'+wdid+'</lexdo:firstAuLoc>\n'
                outfile.write(line)
        elif aulocmatch == None and arlocmatch != None:
            print(arlocmatch.group(2))
            wdjsonsource = requests.get(url='https://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&format=json&titles='+arlocmatch.group(2))
            wdjson =  wdjsonsource.json()
            entities = wdjson['entities']
            for wdid in entities:
                print(wdid)
                line = arlocmatch.group(1)+'<lexdo:articleLoc>http://wikidata.org/entity/'+wdid+'</lexdo:articleLoc>\n'
                outfile.write(line)
        else:
            outfile.write(line)
