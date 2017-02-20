import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def audit_unicode_name(element_attrib):
	u = element_attrib.encode("utf-8")
	if(str(u) == str("b\'IbnT\\xc4\\x93\\xc5\\xa1f\\xc4\\xabn\'")):
		return "IbnTesfin"
	elif(str(u) == str("b\'Walter Schl\\xc3\\xb6gl\'")):
		return "Walter Schlogl"
	elif(str(u) == str("b\'\\xe0\\xa4\\xb6\\xe0\\xa4\\x82\\xe0\\xa4\\xa4\\xe0\\xa4\\xa8\\xe0\\xa5\\x82\'")):
		return "Shantanu"
	elif(str(u) == str("b\'\\xd8\\xb9\\xd9\\x82\\xd8\\xa8\\xd8\\xa9 \\xd8\\xa8\\xd9\\x86 \\xd9\\x86\\xd8\\xa7\\xd9\\x81\\xd8\\xb9\'")):
		return "Uqba"
	else :
		return element_attrib


def audit_country_state_city(tag_attrib_k,tag_attrib_v):
	if(tag_attrib_k == "addr:country" and tag_attrib_v == "IN"):
		return "India"
	elif(tag_attrib_k == "addr:state" and tag_attrib_v == "MH"):
        	return "Maharashtra"
	elif(tag_attrib_k == "addr:city" and tag_attrib_v != "Pune"):
		return "Pune"
	return tag_attrib_v


def audit_brand(tag_attrib_v):
	if tag_attrib_v == "HPCL":
		return "Hindustan Petroleum Corporation Limited"
	elif tag_attrib_v == "BPCL":
		return "Bharat Petroleum Corporation Limited"
	elif tag_attrib_v == "IOCL":
		return "Indian Oil Corporation Limited"
	elif tag_attrib_v == "MNGL":
		return "Maharashtra Natural Gas Limited"
	return tag_attrib_v



def shape_element(element):
    node = {}
    address = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node["type"] = element.tag
        node["created"] = {}
        if "id" in element.attrib:
            node["id"] = element.attrib["id"]
        if "visible" in element.attrib:
            node["visible"] = element.attrib["visible"]
        for created_ele in CREATED:
            if created_ele in element.attrib:
            	if created_ele == "user":
            		node["created"][created_ele] = audit_unicode_name(element.attrib[created_ele])
            	else:
                	node["created"][created_ele] = element.attrib[created_ele]
        if "lat" in element.attrib and "lon" in element.attrib:
            node["pos"] = []
            node["pos"].append(float(element.attrib["lat"]))
            node["pos"].append(float(element.attrib["lon"]))
        
        for tag in element.iter():
            if tag.tag == "tag":
                if ("addr:" in tag.attrib["k"]) and (len(tag.attrib["k"].split(":"))==2):
                	address[tag.attrib["k"].split(":")[-1]] = audit_country_state_city(tag.attrib["k"],tag.attrib["v"])
                	node["address"] = address
                elif("postal_code" in tag.attrib["k"]):
                    node[tag.attrib["k"]] = tag.attrib["v"].replace(" ","")
                elif(":" not in tag.attrib["k"]):
                	if tag.attrib["k"] == "brand":
                		node[tag.attrib["k"]] = audit_brand(tag.attrib["v"])
                	else:
                		node[tag.attrib["k"]] = tag.attrib["v"]
            if tag.tag == "nd" :
            	if "node_refs" not in node.keys():
            		node["node_refs"] = []
            	node["node_refs"].append(tag.attrib["ref"])
        # print(node)
        return node
    else:
    	return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE  : if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('interpreter.osm', False)
    # pprint.pprint(data)

if __name__ == "__main__":
    test()