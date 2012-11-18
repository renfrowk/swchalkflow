

# usage svgMerge.py savedFile outputFile

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

savedF = open(sys.argv[1], 'r')
savedLines = savedF.readlines()

outputF = open(sys.argv[2], 'w')

savedGs = parseGs(savedLines)[0]

gBounds = getTagBounds(savedLines, "<g", "</g>")
prefix = savedLines[0:gBounds[0]['start']]
suffix = savedLines[gBounds[-1]['end']+1:]

mergedDocLines = []

mergedDocLines.append('  <g\n')
mergedDocLines.append('    inkscape:label="Chalkflow_Merged"\n')
mergedDocLines.append('    inkscape:groupmode="layer"\n')
mergedDocLines.append('    id="layer1">\n')

for path in savedGs['paths']:
    mergedDocLines += path['strings']

mergedDocLines.append('  </g>\n')

output = prefix + mergedDocLines + suffix

pprint(output)

for line in output:
    outputF.write(line)
    
outputF.close()
