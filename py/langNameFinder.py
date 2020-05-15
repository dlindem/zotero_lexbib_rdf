from flashtext import KeywordProcessor
keyword_processor = KeywordProcessor()

#get language uri,label@en csv
import csv
with open('E:\lexvo-iso639-3_english_labels.csv', encoding="utf-8") as infile:
	reader = csv.reader(infile)
	langdict = dict((rows[0],[rows[1]]) for rows in reader)
# print(langdict)

#feed language table to flashtext
keyword_processor.add_keywords_from_dict(langdict)

#get vocbench csv


#extract keywordset from text, in order of frequence, sub-order appeareance
text = 'Hello, I speak English, Spanish, and Basque, and I have some notion of German. Do I know German? Yes, I know some German...'
keywords = keyword_processor.extract_keywords(text)
keywordsfreqsort = sorted(keywords,key=keywords.count,reverse=True)
used = set()
keywordset = [x for x in keywordsfreqsort if x not in used and (used.add(x) or True)]

# result
print(keywordset)
