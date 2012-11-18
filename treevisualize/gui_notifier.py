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
import os
import tempfile
import shutil
import subprocess

# Import modules for CGI handling 
import cgi, cgitb 

#clones local repo to temp repo in temp directory. returns content of
#   svg file specified by SVG_PATH and SVG_NAME
# input: commit, hash of git commit snapshot to checkout
#        tmp_dir, temporary directory generated in getSVGFromHash()
# output: svg file contents
def cloneTempRepo(commit, tmp_dir):
	LOCAL_REPO_DIR = "/home/krenfrow/swchalkflow/"
	SVG_PATH = "/svg_diff/test/" #relative to repo root dir
	SVG_NAME = "a.svg"
	
	#load local repo
	local_repo = Repo(LOCAL_REPO_DIR, odbt=GitDB) #open the local git repo
	assert local_repo.bare == False #assert that git repo already exists
	local_repo.config_reader() #read-only access
	
	#ensure tmp_dir exists
	assert os.path.exists(tmp_dir) == True #ensure dir exists
	
	#clone local repo into temp repo
	temp_repo = local_repo.clone(tmp_dir)
	
	#checkout from commit hash
	temp_repo.git.checkout(commit)
	
	f = open(tmp_dir + SVG_PATH + SVG_NAME, 'r')
	return f.read()

# prints file contents of svg file (hard coded atm) from git snapshot
#    defined by commit hash
# input: commit, commit, hash of git commit snapshot to checkout
# output: prints contents of svg file
def getSVGFromHash(commit):
	try:
		tmp_dir = tempfile.mkdtemp() # create temp dir
		print cloneTempRepo(commit, tmp_dir)
	finally:
		try:
			shutil.rmtree(tmp_dir) # delete directory
		except OSError, e:
			if e.errno != 2: # code 2 - no such file or directory
				raise

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

# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from get fields
command = form.getvalue('command')

print "Content-type:text/html\r\n\r\n"

if (command == 'get_tree_data'):
    repoDirectory = '/home/tomlinson/swchalkflow/'
    
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
        
    hashFileF = open('graphData.hash', 'w')
    hashFileF.write(hashlib.sha224(graphData).hexdigest())
    hashFileF.close()
    print graphData
        
if (command == 'poll_tree_change'):
    
    repoDirectory = '/home/tomlinson/swchalkflow/'
    
    repo = Repo(repoDirectory, odbt=GitDB) #open the local git repo
    assert repo.bare == False #assert that git repo already exists
    repo.config_reader() #read-only access
    
    commit_tree = defaultdict(list) #initialize empty list default dict
    
    #iterate over all branches
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
        print "no_update"

if (command == 'view'):
    form = cgi.FieldStorage()
    hexsha = form.getvalue('hexsha')
    print 'VIEW ' + hexsha
    svg_file = getSVGFromHash(hexsha) #svg_file will be string of file contents
    # set head to hexsha, open inkscape with document (with listener)
    
if (command == 'diff'):
    form = cgi.FieldStorage()
    hexsha_orig = form.getvalue('hexsha_orig')
    hexsha_new = form.getvalue('hexsha_new')
    print 'DIFF ' + hexsha_orig + ' -> ' + hexsha_new
    svg_orig = getSVGFromHash(hexsha_orig)
    svg_new = getSVGFromHash(hexsha_new)
    # compute diff, open inkscape window (with listener)
    
    #run shell command
    cmd = shlex.split(("inkscape -g -f %s") % (filename))
    subprocess.call(cmd)
