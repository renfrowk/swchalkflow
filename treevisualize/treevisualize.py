#!/usr/bin/env python

from git import *
from pprint import pprint
from collections import defaultdict
import json
import os

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

# generate list of commit tree for D3 graph
def graphList(tree):
	out = "["
	for parent, children in tree.items():
		for child in children:
			if child != []:
				out += "{\"source\": \"%s\", \"target\": \"%s\", \"type\": \"suit\"}," % (parent[:6], child[:6])
	out = out[:-1] #remove trailing comma
	out += "]"
	return out

# generate node rels for Graphviz dot file
def diGraph(tree):
	out = ""
	for parent, children in tree.items():
		for child in children:
			if child != []:
				out += "\"%s\" -> \"%s\";\n" % (parent[:6], child[:6])
	return out
	

if __name__ == '__main__':
	LOCAL_REPO_DIR = "/home/krenfrow/swchalkflow/"
	PATH_TO_GRAPH = "treevisualize/" #relative to local repo
	
	repo = Repo(LOCAL_REPO_DIR, odbt=GitDB) #open the local git repo
	assert repo.bare == False #assert that git repo already exists
	repo.config_reader() #read-only access
	
	commit_tree = defaultdict(list) #initialize empty list default dict
	
	#iterate over all branches
	for branch in repo.branches:
		child = repo.commit(branch.name) #get latest commit
		commit_tree[child.hexsha].append([]) #add base as parent with no children
		addNode(child, commit_tree)
	
	#save to chalktreelist.txt
	f_path = LOCAL_REPO_DIR + PATH_TO_GRAPH + "chalktreelist.txt"
	#remove existing
	if os.path.exists(f_path) == True:
		os.remove(f_path)
	f = open(f_path, 'w+')
	f.write(graphList(commit_tree))
	f.close()
	

