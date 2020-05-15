#get language uri,label@en csv
import csv
with open('lexvo-iso639-3_english_labels.csv', encoding="utf-8") as infile:
	reader = csv.reader(infile)
	langdict = dict((rows[0],[rows[1]]) for rows in reader)
# print(langdict)
