import re
import unidecode

def getWbProp(zp, val):
	if zp == "title":
		return [{"property":"P6", "string":val}]
	elif zp == "container-title":
		return [{"property":"P8", "string":val}]
	elif zp == "event":
		return [{"property":"P37", "string":val}]
	elif zp == "page":
		return [{"property":"P24", "string":val}]
	elif zp == "publisher":
		return [{"property":"P34", "string":val}]
	elif zp == "DOI":
		if "http" not in val:
			val = "http://doi.org/"+val
		return [{"property":"P17", "string":val}]
	elif zp == "ISSN":
		if "-" not in val:
			val = val[0:4]+"-"+val[4:9]
		return [{"property":"P20", "string":val[:9]}]
	elif zp == "ISBN":
		val = val.replace("-","")
		val = re.search(r'^\d+',val).group(0)
		if len(val) == 10:
			return [{"property":"P19", "string":val}]
		elif len(val) == 13:
			return [{"property":"P18", "string":val}]
	elif zp == "volume" and item['type'] == "article-journal": # volume only for journals (book series also have "volume")
		return [{"property":"P22", "string":val}]
	elif zp == "issue" and item['type'] == "article-journal": # issue only for journals
		return [{"property":"P23", "string":val}]
	elif zp == "id":
		val = "http://lexbib.org/zotero/"+re.search(r'items/(.*)', val).group(1)
		return [{"property":"P16", "string":val}]
	elif zp == "URL":
		return [{"property":"P21", "string":val}]
	elif zp == "issued":
		year = val["date-parts"][0][0]
		return [{"property":"P14", "string":year}]
	elif zp == "author" or zp == "editor":
		if zp == "author":
			prop = "P39"
		elif zp == "editor":
			prop = "P42"
		creators = []
		listpos = 1
		for creator in val:
			if "non-dropping-particle" in creator:
				creator["family"] = creator["non-dropping-particle"]+" "+creator["family"]
			creators.append({"property":prop, "string":creator["given"]+" "+creator["family"],"Qualifiers":{"P33":str(listpos),"P40":creator["given"],"P41":creator["family"]}})
			listpos += 1
		return creators
