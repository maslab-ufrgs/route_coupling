#takes an csv file as input in the following format
#Instance	Index	PathIndex	PathSize	PathWGHT	cpl	cplDist	Path
#SiouxFalls	1	1	1	6	2.581	2.539	2->1
#and convert to default route file

import sys

def convertToLinkList(stringinput):
    tokens = stringinput.split("->")
    out = ''
    for i in range(len(tokens)):
        if i < len(tokens)-1:
            if i > 0 :
                out += " "
            out += tokens[i] + '-' + tokens[i+1]
    return out

if __name__=="__main__":
    if len(sys.argv) < 2:
        print "convertfernando.py input"
    inputfilename = sys.argv[1]

    #route key is source-destination OD pair
    routes = {}

    for line in open(inputfilename).readlines()[1:]:
        tokens = [ x  for x in  line.replace("\n","").replace("\t",",").replace(" ", ",").split(",") if x != '']
        weight = tokens[4]
        path = convertToLinkList(tokens[-1])
        O = path.split("-")[0]
        D = path.split("-")[-1]
        key = O+'|'+D
        if key not in routes.keys():
            routes[key] = []
        routes[key].append((path, float(weight)))

    outputfilename = inputfilename + 'out'

    filedesc = open(outputfilename, 'w')
    filedesc.write('NODs: %d\n' % len(routes.keys()))
    for odpair in routes.keys():
        filedesc.write('\nODName: %s\n' % odpair)
        filedesc.write('NSPs: %d\n' % len(routes[odpair]))
        filedesc.write('DEMAND: 0\n')
        for (path,weight) in routes[odpair]:
            filedesc.write(path + '\n')
            filedesc.write('%f\n' % weight)
    filedesc.close()

