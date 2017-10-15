#!/usr/bin/python
##This module calculates the shortest paths with KSP and generates an output file with these routes and demand information
#for every od pair
import sys
import OD
'''
Calculates route files from a network file
calculateRoutes.py inputnet k outputfile
'''
if __name__=="__main__":
    if len(sys.argv) < 4:
        print "calculateRoutes.py inputnet k outputfile"
        sys.exit(1)
    ODs = OD.ODSet(int(sys.argv[2]))
    ODs.calculateKSProutes(sys.argv[1])
    ODs.writeRoutesToFile(sys.argv[3])
