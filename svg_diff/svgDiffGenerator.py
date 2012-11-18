

# usage svgDiffGenerator.py origionalFile newFile diffFile(output) // will create diffFile

from pprint import pprint

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

import sys

origF = open(sys.argv[1], 'r')
origLines = origF.readlines()

newF = open(sys.argv[2], 'r')
newLines = newF.readlines()

orig = parseGs(origLines)[0]
new = parseGs(newLines)[0]

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

output = prefix + addedDocLines + deletedDocLines + unchangedDocLines + suffix

pprint(output)

outputF = open(sys.argv[3], 'w')

for line in output:
    outputF.write(line)
    
outputF.close()
