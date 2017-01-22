import sys
import numpy as np


if __name__=="__main__":
    if len(sys.argv) < 2:
        print "coupling2.py <coupling output file>"
        sys.exit(1)
f = open(sys.argv[1])
lines = [x.replace("\n","") for x in  f.readlines()[1:]]

routenames = []
hopmetrics = []
ffttmetrics = []

HOPsum = 0.0
ffttsum = 0.0
for line in lines:
    tokens = line.split(" ")
    routenames.append(tokens[0])
    hopmetric = float(tokens[1])
    hopmetrics.append(hopmetric)
    HOPsum += hopmetric
    ffttmetric = float(tokens[2])
    ffttmetrics.append(ffttmetric)
    ffttsum += ffttmetric

HOPaverage = HOPsum / len(lines)
ffttaverage = ffttsum / len(lines)

outputfile = open(sys.argv[1]+".statistics",'w')
outputfile.write("HOP sum %f\n" % HOPsum)
outputfile.write("HOP AVG %f\n" % HOPaverage)
outputfile.write("HOP MAX %f\n" % max(hopmetrics))
outputfile.write("fftt sum %f\n" % ffttsum)
outputfile.write("fftt AVG %f\n" % ffttaverage)
outputfile.write("fftt MAX %f\n" % max(ffttmetrics))

outputfile.close()

import matplotlib.pyplot as plt

plt.hist(hopmetrics)
plt.title("Hop Coupling Histogram")
plt.xlabel("Hop Coupling")
plt.ylabel("Frequency")
plt.savefig(sys.argv[1]+ ".hopHistogram.png")
plt.close()
plt.hist(ffttmetrics)
plt.title("FFTT Coupling Histogram")
plt.xlabel("FFTT Coupling")
plt.ylabel("Frequency")
plt.savefig(sys.argv[1]+ ".ffttHistogram.png")
