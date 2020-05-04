import json
import spacy
sp = spacy.load('en_core_web_sm')

with open("E:/results.json", encoding="utf-8") as f:
	data =  json.load(f, encoding="utf-16")
results = data['results']
bindings = results['bindings']

for item in bindings:
	if 'authorsJson' in item:
		authorsJson = item['authorsJson']
		authorsliteral = authorsJson['value']
		authors = json.loads(authorsliteral)
		item['authorsJson'] = authors
		item['authors'] = item.pop('authorsJson')
	if 'uri' in item:
		uri = item['uri']['value']
		item['uri'] = uri
	if 'title' in item:
		title = item['title']['value']
		item['title'] = title
	if 'pubTM' in item:
		pubTM = item['pubTM']['value']
		item['pubTM'] = pubTM
	# adding '?usenewlibrary=0' to Zotero Links
	if 'sourceUri' in item:
		sourceUri = item['sourceUri']['value']+'?usenewlibrary=0'
		item['sourceUri'] = sourceUri
	if 'sourceTitle' in item:
		sourceTitle = item['sourceTitle']['value']
		item['sourceTitle'] = sourceTitle
	if 'lang' in item:
		lang = item['lang']['value']
		item['lang'] = lang[-3:]
	if 'body' in item and lang[-3:] == 'eng':
		bodytext = item['body']['value']
		item['body'] = bodytext
		bodylem = ""
		for word in sp(bodytext):
			bodylem+=("%s " % word.lemma_)
		item['bodylem'] = bodylem
		


with open('E:\processed.json', 'w') as json_file:
	json.dump(bindings, json_file, indent=2)

