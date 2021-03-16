# creates bibitem labels from publication title (lable language = publication language of the article)
import time
import requests
import lwb

print('Will now check if there are any BibItems without English label...')
# get bibitems without label (bibitems_titles_langs.rq)
url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20distinct%20%3FbibItem%20%3Fdct_title%20%3Fwikilang%20where%0A%7B%20%3FbibItem%20ldp%3AP5%20lwb%3AQ3%20.%0A%20MINUS%20%7B%3FbibItem%20rdfs%3Alabel%20%3Flabel%20FILTER%20%28lang%28%3Flabel%29%3D%22en%22%29%7D%0A%20%3FbibItem%20ldp%3AP6%20%3Fdct_title%20.%0A%20%3FbibItem%20ldp%3AP11%20%3Fpublang%20.%0A%20%3Fpublang%20ldp%3AP43%20%3Fwikilang%20.%0A%7D"
done = False
while (not done):
	try:
		r = requests.get(url)
		bindings = r.json()['results']['bindings']
	except Exception as ex:
		print('Error: SPARQL request failed: '+str(ex))
		time.sleep(2)
		continue
	done = True
#print(str(bindings))

print('Found '+str(len(bindings))+' BibItems without label. Will proceed to set them using the BibItem title...\n')
time.sleep(3)

count = 0
for item in bindings:
	count +=1
	bibitem = item['bibItem']['value'].replace("http://data.lexbib.org/entity/","")
	title = item['dct_title']['value']
	wikilang = item['wikilang']['value']
	label = lwb.setlabel(bibitem,wikilang,title)
	if wikilang != "en": # always add title as English label, also if not English
		label = lwb.setlabel(bibitem,"en",title)
	if label:
		print('OK. '+str(len(bindings)-count)+' items left.\n')
