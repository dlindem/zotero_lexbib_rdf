import json
import re
import mwclient
import time

# LexBib wikibase OAuth
site = mwclient.Site('www.wikidata.org')
with open('D:/Lab_LAR/Wikidata/pwd.txt', 'r', encoding='utf-8') as pwdfile:
    pwd = pwdfile.read()
def get_token():
    print('Getting fresh login token...')
    login = site.login(username='DL2204', password=pwd)
    csrfquery = site.api('query', meta='tokens')
    token=csrfquery['query']['tokens']['csrftoken']
    print("Got CRSF Token: "+token)
    return token
token = get_token() # get first new token

with open ('D:/Lab_LAR/TLex/LAR Basque v5 wikidata.csv', 'r', encoding='utf-8') as file:
    tlex = file.read().split('\n')

#print(str(tlex))
errorlog = []
edits = 0
rowcount = 0

for row in tlex:

    rowcount += 1
    wdlexemelink = re.search('(http://www.wikidata.org/entity/L\d+)', row).group(1)
    print('\nRow ['+str(rowcount)+']: '+wdlexemelink)
    wdlexemeId = wdlexemelink.replace('http://www.wikidata.org/entity/', '')
    lemgroup = row.split(wdlexemelink)[0]
    #print(lemgroup)
    lemma = '"'+lemgroup.split(',')[1]+'"' # takes one of the unidecode versions
    #print(lemma)
    linkgroup = row.split(wdlexemelink)[1]
    #print(linkgroup)
    links = re.findall(r'http[^,]+', linkgroup)
    #print(str(links))

    # check if "attested in Larramendi" is already claimed
    results = site.api('wbgetclaims', entity=wdlexemeId, property='P5323')
    if 'claims' in results and 'P5323' in results['claims']:
        for result in results['claims']['P5323']:
            foundobj = result['mainsnak']['datavalue']['value']['id']
            guid = result['id']
            print(foundobj+', GUID '+guid)
            if '65216433' in foundobj:
                print('Found redundant Object "65216433". Will skip this.')
                time.sleep(5)
    else:

    # write "attested in" statement if not already there
        results = site.post('wbcreateclaim', token=token, entity=wdlexemeId, property='P5323', snaktype="value", value='{"entity-type":"item","numeric-id":65216433}')
        if results['success'] == 1:
            print('Wb create claim for '+wdlexemelink+' "attested in Larramendi": success.')
            edits += 1
            time.sleep(2)
        else:
            print('*** *** Wbcreateclaim for '+wdlexemelink+' "attested in Larramendi": *** Unknown error not raised to exception.')


    # check for present qualifiers in attested-in-Larramendi-claim
    results = site.api('wbgetclaims', entity=wdlexemeId, property='P5323')
    if 'claims' in results and 'P5323' in results['claims']:
        for result in results['claims']['P5323']:
            foundobj = result['mainsnak']['datavalue']['value']['id']
            guid = result['id']
            print(foundobj+', GUID '+guid)
            if '65216433' in foundobj:
                print('Found "attested in Larramendi". Will now write qualifiers.')
                #print(str(results))
                results = site.post('wbsetqualifier', token=token, claim=guid, property='P7855', snaktype='value', value=lemma)
                if results['success'] == 1:
                    print('Wb create claim for '+wdlexemelink+' "attested as" (lemma): '+lemma+': success.')
                    edits += 1
                    time.sleep(2)
                else:
                    print('*** *** Wbcreateclaim for '+wdlexemelink+' "attested as" (lemma): '+lemma+' *** Unknown error not raised to exception.')

                for item in links:
                    try:
                        print('Will now write claim "described at URL": '+item)
                        link = '"'+item+'"'
                        results = site.post('wbsetqualifier', token=token, claim=guid, property='P973', snaktype='value', value=link)
                    except Exception as ex:
                        print(str(ex))
                        time.sleep(5)
                        pass
                    if results['success'] == 1:
                        print('Wb create claim for '+wdlexemelink+' "described at URL": '+link+': success.')
                        edits += 1
                        time.sleep(2)
                    else:
                        print('*** *** Wbcreateclaim for '+wdlexemelink+' "attested as" (lemma): '+lemma+' *** Unknown error not raised to exception.')
            else:
                print('*** ERROR: Das kann nicht sein. Angeblich gibt es das claim nicht.')


print ('Finish. '+str(edits)+' edits made.')
