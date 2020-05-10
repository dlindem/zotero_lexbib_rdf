import json
import spacy
sp = spacy.load('en_core_web_sm')

with open("D:/Lab_LexDo/100520/result.json", encoding="utf-8") as f:
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
	if 'articleTM' in item:
		articleTM = item['articleTM']['value']
		item['articleTM'] = articleTM
	# adding '?usenewlibrary=0' to Zotero Links
	if 'sourceUri' in item:
		sourceUri = item['sourceUri']['value']+'?usenewlibrary=0'
		item['sourceUri'] = sourceUri
	if 'sourceTitle' in item:
		sourceTitle = item['sourceTitle']['value']
		item['sourceTitle'] = sourceTitle
	if 'publang' in item:
		lang = item['publang']['value']
		item['lang'] = lang[-3:]
	bodytext = ""
	# check if text is English and txt-object exists
	if lang [-3:] == 'eng' and 'pdftxt' in item:
		txtpath = item['pdftxt']['value']
		try:
			with open(txtpath, 'r', encoding="utf-8") as txtfile:
				bodytext = txtfile.read()
			item['body'] = bodytext
		except IOError:
			print(title+" "+txtpath+" not accessible")
	else:
		print(title+" is "+lang+" ...aborted")
	# if fulltext was not English or not found, use english abstract (if exists)
	if bodytext == "" and 'abstracttext' in item and item['abstractlang']['value'][-3:] == 'eng':
		bodytext = item['abstracttext']['value']
		item['body'] = bodytext
		print(" - got abstract text instead")
	elif bodytext == "":
		print(" - found no English abstract")
	# lemmatize english text or abstract
	bodylem = ""
	for word in sp(bodytext):
		bodylem+=("%s " % word.lemma_)
	item['bodylem'] = bodylem
		


with open('D:/Lab_LexDo/100520/processed.json', 'w') as json_file:
	json.dump(bindings, json_file, indent=2)

