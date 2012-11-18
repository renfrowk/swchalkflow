#!/usr/bin/env python

# usage gui_notifier.py
# reads directory name from a file in this dir, gitRepo.dir
# generates a file, graphData.hash, in the current directory, to store hash of git tree data to avoid resending to gui

from git import *
from pprint import pprint
from collections import defaultdict
import json
import hashlib
import cgi

# Import modules for CGI handling 
import cgi, cgitb 

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

def graphList(tree):
	out = "["
	for parent, children in tree.items():
		for child in children:
			if child != []:
				out += "{source: \"%s\", target: \"%s\", type: \"suit\"}," % (parent[:6], child[:6])
	out += "]"
	return out

# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from get fields
command = form.getvalue('command')

print "Content-type:text/html\r\n\r\n"

if (command == 'poll_tree_change'):
    
    repoDirF = open('gitRepo.dir', 'r')
    repoDirectory = repoDirF.read()
    repoDirF.close()
    
    repo = Repo(repoDirectory, odbt=GitDB) #open the local git repo
	assert repo.bare == False #assert that git repo already exists
	repo.config_reader() #read-only access
	
	commit_tree = defaultdict(list) #initialize empty list default dict
	
	#iterate over all branches
	#for each branch - needs implementation
	for branch in repo.branches:
		child = repo.commit(branch.name) #get latest commit
		commit_tree[child.hexsha].append([]) #add base as parent with no children
		addNode(child, commit_tree)
	
    graphData = graphList(commit_tree)
	graphDataHash = hashlib.sha224(graphData).hexdigest()
    
    hashFileF = open('graphData.hash', 'r')
    storedHash = hashFileF.read()
    hashFileF.close()
    
    if (graphDataHash != storedHash):
        hashFileF = open('graphData.hash', 'w')
        hashFileF.write(hashlib.sha224(graphData).hexdigest())
        hashFileF.close()
        print graphData
    else:
        print "{'update':'false'}"

if (command == 'view'):
    form = cgi.FieldStorage()
    hexsha = form["hexsha"]
    # set head to hexsha, open inkscape with document (with listener)
    
if (command == 'diff'):
    form = cgi.FieldStorage()
    hexshaOrig = form["hexsha_orig"]
    hexshaNew = form["hexsha_new"]
    # compute diff, open inkscape window (with listener)
    
