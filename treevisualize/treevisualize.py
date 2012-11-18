#!/usr/bin/env python

from git import *
from pprint import pprint
from collections import defaultdict
import json

def addNode(child, tree):
	#base case
	if not child.parents:
		tree["top"].append(child.hexsha)
		return
	
	for parent in child.parents: #iterate over each child's parent
		parent_id = parent.hexsha
		child_id = child.hexsha
		
		tree[parent_id].append(child_id)
		addNode(parent, tree)

#depreciated
def jsonify(tree):
	out = json.dumps(tree, sort_keys=True, indent=4)
	return out

#depreciated	
def d3json(tree):
	out = ""
	#find head
	for top in tree["top"]:
		out += d3node(top, tree) + ","
	return out

#depreciated
def d3node(node, tree):
	if node == []: #base case
		return ""

	out = "{\"name\": \"" + node[:4] + "\","
	out += "\"children\": ["
	
	for child in tree[node]:
		out += d3node(child, tree) + ","
	out += "]"
	out += "}"
	return out
	
def graphList(tree):
	out = "["
	for parent, children in tree.items():
		for child in children:
			out += "{source: \"%s\", target: \"%s\", type: \"suit\"}," % (parent[:6], child[:6])
	out += "]"
	return out

if __name__ == '__main__':
	repo = Repo("~/swchalkflow/", odbt=GitDB) #open the local git repo
	assert repo.bare == False #assert that git repo already exists
	repo.config_reader() #read-only access
	
	commit_tree = defaultdict(list) #initialize empty list default dict
	
	#iterate over all branches
	#for each branch - needs implementation
	
	child = repo.commit('master') #get latest commit
	
	commit_tree[child.hexsha].append([]) #add base as parent with no children
	
	addNode(child, commit_tree)
	
	print graphList(commit_tree)
	

