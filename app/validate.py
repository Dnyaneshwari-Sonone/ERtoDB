'''
Python code that takes a JSON file (assumed to be coming from the diagrammer)
and checks whether all constraints / database rules are followed.
'''
import json, pdb, ast
from .generator import *
from .normalize import *

# with open("../data/dummy.json") as data_file:
# 	data = json.load(data_file)

def validate(data, flag):
	data = json.loads(data)
	errors = []
	# First, validate FK->PK constraint
	# This involves:
	# a) ensuring that the FK and PK exist in respective tables
	# b) the types of the two columns are the same
	relation_list = data["relations"]

	# Add an error if there are duplicate relations
	temp = [str(item) for item in relation_list]
	if len(temp) != len(set(temp)):
		errors.append("Duplicate relations exist!")
		
	entity_list = data["entities"]
	for relation in relation_list:
		fromTable = relation["from"]
		toTable = relation["to"]
		fromAttrs = relation["FK"].split(",")
		fromAttrs =[ s for s in fromAttrs if s != '' ]
		toAttrs = relation["PK"].split(",")
		toAttrs =  [s for s in toAttrs if s != '' ]
		fromNotFound = toNotFound = True
		fromTypes = ["" for x in range(len(fromAttrs))]
		toTypes = ["" for x in range(len(toAttrs))]

		for entity in entity_list:
			if entity["name"] == fromTable:
				fromNotFound = False
				for attribute in entity["attributes"]:
					if attribute["name"] in toAttrs:
						fromTypes[toAttrs.index(attribute["name"])] = attribute["datatype"]
						break
			elif entity["name"] == toTable:
				toNotFound = False
				for attribute in entity["attributes"]:
					if attribute["name"] in fromAttrs:
						toTypes[fromAttrs.index(attribute["name"])] = attribute["datatype"]
						break
		if len(fromAttrs) != len(toAttrs):
			errors.append("Number of FKs and PKs doesn't match!")
		if fromNotFound == True:
			errors.append("Foreign key table ({0}) not found!".format(fromTable))
		if toNotFound == True:
			errors.append("Referenced PK table ({0}) not found!".format(toTable))
		if fromTypes != toTypes:
			errors.append("FK ({0}) and PK ({1}) types don't match!".format(fromTable+"."+str(fromAttrs), toTable+"."+str(toAttrs)))

	# validate()
	err_string = ''
	if len(errors):
		# print "ERRORS:"
		for idx, error in enumerate(errors):
			err_string += error

	if err_string == '':
		if flag == 0:
			return generate(data)
		elif flag==1:
			normalized_data = ret_normalize(data)
			return generate(json.loads(normalized_data))
		else:
			return ret_normalize(data)
	else:
		return err_string