#!/usr/bin/python
import sys
import OD

'''
Calculates coupling function over network
Inputs:
    nfile: network file
    rfile: route file
        one of the last two MUST be defined
    sfile: simulation output file
    k: k parameter for ksp
Outputs:
    csv file with data
'''
def calculate_coupling(nfile, rfile, sfile, k, edge_list=None, node_list=None, od_matrix=None,
                       output=False):
    ODs = OD.ODSet(k)
    if rfile is not None :
        network_filename = [x for x in rfile.split('/') if x != ''][-1]
        network_name = network_filename.split('.')[0]
        #route file was provided no need to calculate routes
        ODs.loadRoutesFromFile(rfile)
    elif edge_list and node_list and od_matrix:
        network_name = nfile
        #May god bless us all
        ODs.calculateKSProutes(nfile, edge_list=edge_list, node_list=node_list, od_matrix=od_matrix,
                               output=output)
    else:
        network_filename = [x for x in nfile.split('/') if x != ''][-1]
        network_name = network_filename.split('.')[0]
        #need to calculate routes from nfile
        ODs.calculateKSProutes(nfile, output=output)

    rowSPNames   = ODs.getRow_of_SPsNames()
    rowLinkNames = ODs.getUniqueLinkNames()
    output_filename = 'index.html'

    demands = {}
    for i in ODs.getODs():
        route_name = i.name
        route_demand = i.demand
        demands[route_name.strip()] = float(route_demand)


    #------- Reads relevant info from the file with simulation results
    if sfile is None:
        simulation_results_available = False
    else:
        simulation_results_available = True
        simulation_file = open(sys.argv[3], "r")

        tmp = simulation_file.readline() # skips first line of file with simulation results; header is in the 2nd one
        simulation_headers = simulation_file.readline()
        simulation_headers = simulation_headers.split()
        nDriversPerLink_indices = [i for i in range(len(simulation_headers)) if simulation_headers[i].startswith('nd_')]


        for line in simulation_file:
            pass # skips all lines of the file, then reads the last one (last state of the system, at convegence)
        lastLineOfResults = line.split()
        nDriversPerLink = {}
        for i in nDriversPerLink_indices:
            linkName = simulation_headers[i][3:]
            nDriversPerLink[linkName] = float(lastLineOfResults[i])

        SPNames_header=simulation_headers[-len(rowSPNames[1:]):]
        regex = re.compile(r'(.*)to(.*)_(.*)') # first group is origin node of a SP, second is destination, third is the # of this SP within the OD
        SPNames_from_simulation = [] # stores SP names as they appear in the simulation file
        for i in SPNames_header:
            tmp = re.match(regex, i)
            SPName = "%s|%s(%s)" % (tmp.group(1).strip(), tmp.group(2).strip(), tmp.group(3).strip())
            SPNames_from_simulation.append(SPName)

        nDriversPerOD = lastLineOfResults[-len(rowSPNames[1:]):] # gets last elements of results line; these are #drivers in each route of each OD
        nDriversPerOD = [float(i) for i in nDriversPerOD] # convert from string to float

    # -------------------------------------------------

    allSPs = ODs.getAllSPs()
    nSPs   = len(allSPs)

    textoutput = open(network_name+'.results.csv','w')
    print(network_name)
    textoutput.write("Route CouplingHop CouplingFFTT\n")
    routeAvgCouplingHOP = {}
    routeAvgCouplingFFTT = {}
    cur_row = 1
    for i in range(nSPs):
        SP1 = allSPs[i]
        row_contents = [rowSPNames[cur_row]]
        sumCouplingsHOP = 0.0
        sumCouplingsFFTT = 0.0
        for j in range(nSPs):
            SP2 = allSPs[j]
            # # don't count coupling of a route with itself when computing mean coupling of a route
            if i!=j:
                sumCouplingsHOP = sumCouplingsHOP + SP1.getHopCoupling(SP2)
                sumCouplingsFFTT = sumCouplingsFFTT + SP1.getFFTTCoupling(SP2)
        # ok to take the average of percentages bc percentages are wrt to the same total (in this case, #links in SP1)
        routeAvgCouplingHOP[rowSPNames[cur_row]] = float(sumCouplingsHOP)/(nSPs-1)  # -1 because we didn't count the route against itself
        routeAvgCouplingFFTT[rowSPNames[cur_row]] = (float(sumCouplingsFFTT) / (nSPs - 1)) * 100
        textoutput.write(rowSPNames[cur_row] +' '+ str(routeAvgCouplingHOP[rowSPNames[cur_row]]) +' '+ str(routeAvgCouplingFFTT[rowSPNames[cur_row]]) +'\n' )
        cur_row = cur_row + 1
    textoutput.close()

if __name__ == "__main__":
    import argparse
    prs = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                  description="""
                                  This script calcultes the coupling of routes in a network""")
    prs.add_argument("-nf", dest="nfile", required=False, help="The network file.\n", default=None)
    prs.add_argument("-rf", dest="rfile", required=False, help="The route file.\n",default=None)
    prs.add_argument("-sr", dest="sfile", required=False, help="Simulation results file.\n",default=None)
    prs.add_argument("-k", dest="k", type=int, default=8,
                     help="'K' parameters for the KSP (K-ShortestPath) Algorithm.\n")

    args = prs.parse_args()

    if args.nfile is None and args.rfile is None:
        prs.error("Either a network file or a route file must be provided")

    else:
        calculate_coupling(args.nfile, args.rfile,args.sfile, args.k)
