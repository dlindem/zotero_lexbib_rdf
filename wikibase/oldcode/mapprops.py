import getqid
import lexvomapping

def getWbProp(zp, val):
	if zp == "type":
		props = []
		if val == "paper-conference":
			props.append({"property":"P5","qid":"Q19"})
		elif val == "article-journal":
			props.append({"property":"P5","qid":"Q21"})
		elif val == "book":
			props.append({"property":"P5","qid":"Q16"})
		elif val == "chapter":
			props.append({"property":"P5","qid":"Q17"})
		elif val == "motion_picture": # videos
			props.append({"property":"P5","qid":"Q25"})
		elif val == "speech":
			props.append({"property":"P5","qid":"Q47"})
		elif val == "thesis":
			props.append({"property":"P5","qid":"Q57"})
		return props
	elif zp == "tags":
		for tag in val:
			if tag["tag"].startswith(':event ') == True:
				event = tag["tag"].replace(":event ","http://lexbib.org/events#")
				qid = getqid.getqid("Q6", event)
				return [{"property":"P36","qid":qid}]
			if tag["tag"].startswith(':container ') == True:
				container = tag["tag"].replace(":container ","")
				if container.startswith('isbn:') or container.startswith('oclc:'):
					container = container.replace("-","")
					container = container.replace("isbn:","http://worldcat.org/isbn/")
					container = container.replace("oclc:","http://worldcat.org/oclc/")
				elif container.startswith('doi:'):
					container = container.replace("doi:", "http://doi.org/")
				qid = getqid.getqid("Q12", container)
				return [{"property":"P9","qid":qid}]
			if tag["tag"].startswith(':type ') == True:
				type = tag["tag"].replace(":type ","")
				if type == "Review":
					return [{"property":"P5","qid":"Q15"}]
				elif type == "Report":
					return [{"property":"P5","qid":"Q46"}]
				elif type == "Proceedings":
					return [{"property":"P5","qid":"Q18"}]
	elif zp == "language":
		language = lexvomapping.getLexvoId(val)
		qid = getqid.getqid("Q8", language)
		return [{"property":"P11","qid":qid}]

	### props with literal value

	elif zp == "title":
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
	elif zp == "volume" and type == "article-journal": # volume only for journals (book series also have "volume")
		return [{"property":"P22", "string":val}]
	elif zp == "issue" and type == "article-journal": # issue only for journals
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
