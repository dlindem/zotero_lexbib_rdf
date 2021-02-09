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
