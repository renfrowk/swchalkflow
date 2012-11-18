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
import sys
import StringIO
import subprocess

# Import modules for CGI handling 
import cgi, cgitb 

#clones local repo to temp repo in temp directory. returns content of
#   svg file specified by SVG_PATH and SVG_NAME
# input: commit, hash of git commit snapshot to checkout
#        tmp_dir, temporary directory generated in getSVGFromHash()
# output: svg file contents
def cloneTempRepo(commit, tmp_dir):
    LOCAL_REPO_DIR = "/home/tomlinson/swchalkflow/"
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
    
    assert os.path.exists(tmp_dir + SVG_PATH) == True #ensure dir exists
    f = open(tmp_dir + SVG_PATH + SVG_NAME, 'r')
    return f.read()

# prints file contents of svg file (hard coded atm) from git snapshot
#    defined by commit hash
# input: commit, commit, hash of git commit snapshot to checkout
# output: prints contents of svg file
def getSVGFromHash(commit):
    try:
        tmp_dir = tempfile.mkdtemp() # create temp dir
        return cloneTempRepo(commit, tmp_dir)
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










def getTagBounds (lineArr, startString, endString):
    
    blocks = []
    startI = []
    endI = []

    for lineNum, line in enumerate(lineArr):
        if(line.find(startString) != -1):
            startI.append(lineNum)
        if(line.find(endString) != -1):
            endI.append(lineNum)

    for i, bla in enumerate(startI):
        blocks.append({'start': startI[i], 'end': endI[i]})
        
    return blocks;

def parseGs (fileArr):

    gBounds = getTagBounds(fileArr, "<g", "</g>");

    #pprint(gBounds)

    gs = []

    #pprint(gBounds)
    for gI,gBound in enumerate(gBounds):
        gString = fileArr[gBound['start']+1:gBound['end']]
        #pprint(gString)
        pathBounds = getTagBounds(gString, "<path", "inkscape:connector-curvature");
        thisG = {'bounds': gBound}
        thisG['paths'] = [];
        for pathBound in pathBounds:
            pathString = gString[pathBound['start']:pathBound['end']+1]
            thisG['paths'].append({'strings': pathString, 'bounds': pathBound, 'id': int(pathString[3][15:19])})
            #pprint(pathString)
        gs.append(thisG)

    return gs

def findPathId(g,pathId):
    for path in g['paths']:
        if (pathId == path['id']):
            return True;
    return False;

def findAdditions(orig, new, added, deleted, unchanged):
    for path in orig['paths']:
        if (findPathId(new, path['id']) == False):
            deleted.append(path)
        else:
            unchanged.append(path)
    for path in new['paths']:
        if (findPathId(orig, path['id']) == False):
            added.append(path)

def generateDiffFile (origString, newString, fileName):

    newStringBuf = StringIO.StringIO(newString)
    origStringBuf = StringIO.StringIO(origString)
    origLines = origStringBuf.readlines()
    newLines = newStringBuf.readlines()

    orig = parseGs(origLines)[0]
    new = parseGs(newLines)[0]

    added = []
    deleted = []
    unchanged = []

    findAdditions(orig, new, added, deleted, unchanged)

    #~ print('ADDED\n')
    #~ pprint(added)

    #~ print('DELETED\n')
    #~ pprint(deleted)

    #~ print('UNCHANGED\n')
    #~ pprint(unchanged)

    gBounds = getTagBounds(origLines, "<g", "</g>")
    prefix = origLines[0:gBounds[0]['start']]
    suffix = origLines[gBounds[-1]['end']+1:]

    addedDocLines = []
    deletedDocLines = []
    unchangedDocLines = []

    unchangedDocLines.append('  <g\n')
    unchangedDocLines.append('    inkscape:label="Chalkflow_Unchanged"\n')
    unchangedDocLines.append('    inkscape:groupmode="layer"\n')
    unchangedDocLines.append('    id="layer1">\n')

    addedDocLines.append('  <g\n')
    addedDocLines.append('    inkscape:label="Chalkflow_Added"\n')
    addedDocLines.append('    inkscape:groupmode="layer"\n')
    addedDocLines.append('    id="layer2">\n')

    deletedDocLines.append('  <g\n')
    deletedDocLines.append('    inkscape:label="Chalkflow_Deleted"\n')
    deletedDocLines.append('    inkscape:groupmode="layer"\n')
    deletedDocLines.append('    id="layer3">\n')

    for path in added:
        addedDocLines += path['strings']
        
    for path in deleted:
        deletedDocLines += path['strings']
        
    for path in unchanged:
        unchangedDocLines += path['strings']

    addedDocLines.append('  </g>\n')
    deletedDocLines.append('  </g>\n')
    unchangedDocLines.append('  </g>\n')

    output = prefix + unchangedDocLines + addedDocLines + deletedDocLines + suffix

    outputF = open(fileName, 'w')

    for line in output:
        outputF.write(line)
        
    outputF.close()
    
    
    




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
    svg_file = getSVGFromHash(hexsha) #svg_file will be string of file contents
    outputF = open('/home/tomlinson/output/'+hexsha+'.svg', 'w')
    outputF.write(svg_file)
    outputF.close()
    
    # set head to hexsha, open inkscape with document (with listener)
    
if (command == 'diff'):
    form = cgi.FieldStorage()
    hexsha_orig = form.getvalue('hexsha_orig')
    hexsha_new = form.getvalue('hexsha_new')
    svg_orig = getSVGFromHash(hexsha_orig)
    svg_new = getSVGFromHash(hexsha_new)
    generateDiffFile(svg_orig, svg_new, '/home/tomlinson/output/'+hexsha_orig+'_'+hexsha_new+'.svg')
    # compute diff, open inkscape window (with listener)
    
    #run shell command
    cmd = shlex.split(("inkscape -g -f %s") % (filename))
    subprocess.call(cmd)
