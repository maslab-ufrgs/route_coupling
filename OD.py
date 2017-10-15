from ksp import KSP

epsilonMultiplier = 0.1
from readUtils import *

'''
Defines OD and network related data structures
'''

class ODSet:
    # initializes network. Loads OD pairs
    # from network file and calculate
    # shortest paths
    def __init__(self, k):
        self.OD_Pairs = []
        self.linksFFTT = dict()
        self.k = k
    ##using the network file and k calculates the shortest
    # paths of every OD pair
    def calculateKSProutes(self, network_filename):
        # open network with ksp
        self.ksp_instance = KSPInstance(network_filename, 0.0)
        #### loads od information
        filen = open(network_filename, 'r')
        for line in filen:
            if line[0:2] == 'od':
                line = line.replace('\n', '')
                tokens = line.split(' ')

                origin = tokens[2]
                destination = tokens[3]
                demand = int(float(tokens[4]))
                if(origin != destination and demand > 0):
                    pair = ODPair(origin, destination, demand, self)
                    pair.calculateKSP(self.k, self.ksp_instance)
                    self.OD_Pairs.append(pair)
        self.linksFFTT = self.ksp_instance.getAllLinksFFTT()
        filen.close()

    def writeRoutesToFile(self, outputfilename):
        fileout = open(outputfilename, 'w')
        fileout.write("NODs: %d\n" % len(self.OD_Pairs))
        for ODp in self.OD_Pairs:
            assert isinstance(ODp, ODPair)
            fileout.write("\nODName: %s\n" % ODp.name)
            fileout.write("NSPs: %d\n" % len(ODp.getSPs()))
            fileout.write("DEMAND: %d\n" % ODp.getDemand())
            for sp in ODp.getSPs():
                fileout.write(sp.__str__() + '\n')
                fileout.write(str(sp.getCost()) + '\n')

        fileout.write("\nNLINKS: %d\n" % len(self.linksFFTT))
        for link in self.linksFFTT.keys():
            fileout.write("LINK: %s %f\n" % (link, self.linksFFTT[link]))

    def loadRoutesFromFile(self, routesfile):
        filedesc = open(routesfile, 'r')
        n_ODPairs = int(readNextWithTag(filedesc, "NODs:"))


        for i in range(n_ODPairs):
            ODName = readNextWithTag(filedesc, "ODName:")
            n_SPs = int(readNextWithTag(filedesc, "NSPs:"))
            demand = int(readNextWithTag(filedesc, "DEMAND:"))
            tokens = ODName.split('|')
            origin = tokens[0]
            destination = tokens[1]
            curOD = ODPair(origin, destination, demand, self)
            splist = []

            for j in range(n_SPs):
                curSPStr = readNext(filedesc)
                linklist = curSPStr.split(" ")
                curSPCost = float(readNext(filedesc))
                splist.append(ShortestPath(ODName + '(' + str(j + 1) + ')', linklist, curSPCost, curOD))
            curOD.loadSPlist(splist)
            self.OD_Pairs.append(curOD)

        n_links = int(readNextWithTag(filedesc, "NLINKS:"))
        for i in range(n_links):
            line = readNextWithTag(filedesc, "LINK:")
            tokens = line.split(" ")
            self.linksFFTT[tokens[0]] = float(tokens[1])

    def getODs(self):
        return self.OD_Pairs

    def getAllSPs(self):
        allSPs = []
        for curOD in self.getODs():
            allSPs.extend(curOD.getSPs())
        return allSPs

    def getRow_of_SPsNames(self):
        allSPs = self.getAllSPs()
        nSPs = len(allSPs)

        rowNames = [""]
        curODName = allSPs[0].getODName()
        curSPindex = 1
        for i in range(nSPs):
            SP1 = allSPs[i]
            if SP1.getODName() == curODName:

                rowNames.append(SP1.name)
            else:
                curODName = SP1.getODName()
                curSPindex = 1

                rowNames.append(SP1.name)
            curSPindex = curSPindex + 1

        rowNames.sort()
        return rowNames

    def getSP_demands(self, demands):
        allSPs = self.getAllSPs()
        nSPs = len(allSPs)

        # gets names of the OD pair of each SP
        ODNames = []
        for i in range(nSPs):
            SP1 = allSPs[i]
            ODNames.append(SP1.getODName())
        ODNames.sort()

        # computes the demand of each OD pair in the above vector
        SPDemands = []
        for i in ODNames:
            SPDemands.append(demands[i])

        return SPDemands

    def getUniqueLinkNames(self):
        allSPs = self.getAllSPs()
        nSPs = len(allSPs)
        linkNames = set()
        for i in range(nSPs):
            linkNames = linkNames.union(set(allSPs[i].getLinks()))
        tmp = list(linkNames)
        tmp.sort()
        return tmp

    def getNumberRoutesEachLinkAppearsIn(self):
        allLinkNames = self.getUniqueLinkNames()
        routesCounter = {}
        for i in allLinkNames:
            routesCounter[i] = 0

        allSPs = self.getAllSPs()
        nSPs = len(allSPs)
        linkNames = set()
        for spIndex in range(nSPs):
            linksInSP = allSPs[spIndex].getLinks()
            for linkName in linksInSP:
                routesCounter[linkName] = routesCounter[linkName] + 1
        return routesCounter

    def getPercentageRoutesEachLinkAppearsIn(self):
        routesCounter = self.getNumberRoutesEachLinkAppearsIn()
        allSPs = self.getAllSPs()
        nSPs = len(allSPs)
        for link in routesCounter:
            routesCounter[link] = 100 * float(routesCounter[link]) / nSPs
        return routesCounter

    def getLinkCoupling(self, routeAvgCoupling):
        # defined as the geometric average of the meanCoupling of each route the link appers in,
        # the meanCoupling is the average coupling of that route wrt all other routes
        # meanCoupling of route R is routeAvgCoupling[R]

        # precisa pegar cada link, e pra cada rota onde ele aparece: acumular routeAvgCoupling[rota] * nLinks[rota]
        # depois dividir por sum_r nLinnks[r]
        #
        # R1: [a b c]
        # R2: [b c f t k p]
        # link b:
        # -> aparece em R1 (com acopl. que eh % wrt nLinksR1=3) e em R2 (com acopl. que eh % wrt nLinks2=6)
        # mediaAcoplamentoRotasOnde_b_aparece: (Ac[R1] * nLinksR1 + Ac[R2] * nLinksR2) / (nLinksR1 + nLinksR2)
        allLinkNames = self.getUniqueLinkNames()
        allSPs = self.getAllSPs()
        nSPs = len(allSPs)

        linksCoupling = {}
        for i in allLinkNames:
            linksCoupling[i] = 0

        for link in allLinkNames:
            sumNLinks = 0  # sum of number of links of all paths where this link shows up
            for spIndex in range(nSPs):
                sp = allSPs[spIndex]
                if link in sp.getLinks():
                    linksCoupling[link] = linksCoupling[link] + routeAvgCoupling[sp.getSPName()] * sp.getSize()
                    sumNLinks = sumNLinks + sp.getSize()
            # print "Before dividing for link %s, coupling is %2.5f" % (link, linksCoupling[link])
            # print "Sum links of routes where it shows up: %d\n" % (sumNLinks)
            linksCoupling[link] = float(linksCoupling[link]) / sumNLinks
        return linksCoupling


class ODPair:
    ##represents each OD pair on the network
    # generates shortest paths from KSP
    def __init__(self, origin, destination, demand, odset):
        self.origin = origin
        self.destination = destination
        self.name = origin + '|' + destination
        self.SPs = []
        self.demand = demand
        self.odset = odset
    def calculateKSP(self, k, ksp_instance):
        # generate paths
        routes = ksp_instance.getRoutes(self.origin, self.destination, k)
        for route_inx, route in enumerate(routes):
            sp = ShortestPath(self.name + '(' + str(route_inx + 1) + ')', route[0], route[1], self)
            self.SPs.append(sp)

    def loadSPlist(self, SPlist):
        self.SPs = SPlist

    def __str__(self):
        out = ''
        for sp in self.SPs:
            out += str(sp) + '\n'
        return out

    def getSP(self, n):
        return self.SPs[n]

    def getSPs(self):
        return self.SPs

    def getDemand(self):
        return self.demand


class ShortestPath:
    def __init__(self, name, link_list, cost, odpair):
        self.name = name
        self.link_list = link_list
        self.cost = cost
        self.odpair = odpair

    def __str__(self):
        return " ".join(self.link_list)

    def getLinks(self):
        return self.link_list

    def getSize(self):
        return len(self.link_list)

    def getCost(self):
        return self.cost

    def getODName(self):
        return self.odpair.name

    def getSPName(self):
        return self.name

    def getCommonLinks(self, otherSP):
        commonLinks = set(self.getLinks()).intersection(set(otherSP.getLinks()))
        return list(commonLinks)

    def getHopCoupling(self, otherSP):
        commonLinks = self.getCommonLinks(otherSP)
        return 100 * float(len(commonLinks)) / len(self.getLinks())



    def getFFTTCoupling(self, otherSP):
        # type: (ShortestPath) -> float
        fFTT_SP = 0.0
        for link in self.getLinks():
            fFTT_SP += self.odpair.odset.linksFFTT[link]

        commonLinks = self.getCommonLinks(otherSP)

        fFTT_SP_otherSP = 0.0
        for link in commonLinks:
            fFTT_SP_otherSP += self.odpair.odset.linksFFTT[link]
        epsilon = epsilonMultiplier * len(self.getLinks())
        return fFTT_SP_otherSP / (fFTT_SP + epsilon)


class KSPInstance:
    def __init__(self, net_filename, KSP_flow=0.0):
        self.V, self.E, OD_list = KSP.generateGraph(net_filename, KSP_flow)
        self.costs = {}
        for link in self.E:
            self.costs[link.name] = link.cost

    def getRoutes(self, origin, destination, k):
        #print origin, destination

        return KSP.getKRoutes(self.V, self.E, origin, destination, k)

    ##return dicitionary with the link name as key and FFTT as value
    ##used only on calculateRoutes.py
    def getAllLinksFFTT(self):
        return self.costs
