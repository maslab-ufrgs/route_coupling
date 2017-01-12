#!/usr/bin/python
import sys
import OD
from prettytable import PrettyTable
import pprint

output_filename = 'index.html'
if __name__=="__main__":
    if len(sys.argv) < 3:
        print "coupling2.py routesfile k"
        sys.exit(1)
    ODs = OD.ODSet(sys.argv[2])
    #ODs.calculateKSP(sys.argv[1], int(sys.argv[2]))
    #ODs.writeRoutesToFile(sys.argv[1]+'.routes.k'+sys.argv[2])
    ODs.loadRoutesFromFile(sys.argv[1])
    rowSPNames   = ODs.getRow_of_SPsNames()
    rowLinkNames = ODs.getUniqueLinkNames()
    print rowSPNames
    print rowLinkNames

    demands = {}
    for i in ODs.getODs():
        route_name = i.name
        route_demand = i.demand
        demands[route_name.strip()] = float(route_demand)


    #------- Reads relevant info from the file with simulation results
    if len(sys.argv)<4:
        simulation_results_available = False
    else:
        simulation_results_available = True
        simulation_file = open(sys.argv[3], "r")

        tmp = simulation_file.readline() # skips first line of file with simulation results; header is in the 2nd one
        simulation_headers = simulation_file.readline()
        simulation_headers = simulation_headers.split()
        #print "opa", len(simulation_headers)
        #print "opa", simulation_headers
        nDriversPerLink_indices = [i for i in range(len(simulation_headers)) if simulation_headers[i].startswith('nd_')]
        #print nDriversPerLink_indices

        for line in simulation_file:
            pass # skips all lines of the file, then reads the last one (last state of the system, at convegence)
        lastLineOfResults = line.split()
        nDriversPerLink = {}
        for i in nDriversPerLink_indices:
            linkName = simulation_headers[i][3:]
            nDriversPerLink[linkName] = float(lastLineOfResults[i])
        print "Drivers per link"
        pprint.pprint(nDriversPerLink)

        SPNames_header=simulation_headers[-len(rowSPNames[1:]):]
        regex = re.compile(r'(.*)to(.*)_(.*)') # first group is origin node of a SP, second is destination, third is the # of this SP within the OD
        SPNames_from_simulation = [] # stores SP names as they appear in the simulation file
        for i in SPNames_header:
            tmp = re.match(regex, i)
            SPName = "%s|%s(%s)" % (tmp.group(1).strip(), tmp.group(2).strip(), tmp.group(3).strip())
            SPNames_from_simulation.append(SPName)

        nDriversPerOD = lastLineOfResults[-len(rowSPNames[1:]):] # gets last elements of results line; these are #drivers in each route of each OD
        nDriversPerOD = [float(i) for i in nDriversPerOD] # convert from string to float
        print "Drivers per OD", nDriversPerOD

    # -------------------------------------------------
    routesfile = open("routes.txt", 'w')
    for pair in ODs.OD_Pairs:
        for sp in pair.SPs:
            links = sp.link_list
            out = []
            last = None
            for i in links:
                for n in i.split('-'):
                    if n!= last:
                        out.append(n)
                        last = n
            routesfile.write('-'.join(out) + '\n')
    routesfile.close()
    '''
    output_file = open(output_filename, 'w')
    output_file.write("<!DOCTYPE html><html><head><style>")
    output_file.write("table, th, td {border: 1px solid black; border-collapse: collapse; text-align: center;}")
    output_file.write("th, td {padding: 3px; text-align: center;} th {text-align: center; background-color: #ff9999;} </style>")
    output_file.write("</head><body><center>")
    '''

    allSPs = ODs.getAllSPs()
    nSPs   = len(allSPs)

    '''
    output_file.write("\n\n<h1> Routes: </h1>\n<table>\n")
    output_file.write("<tr><th>Route Name</th><th>Route Links</th></tr>\n")
    for sp in allSPs:
        output_file.write("<tr><td>%s</td><td>%s</td></tr>\n" % (sp.getSPName(), '  &rarr; '.join(sp.getLinks())))
    output_file.write("</table>\n\n")
    '''
    textoutput = open('out.csv','w')
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
        #inter_route_table.add_row(row_contents)
        cur_row = cur_row + 1
    textoutput.close()

    '''
    # Routes - Mean Coupling - HOP Metric
    route_avg_coupling_table = PrettyTable(rowSPNames[1:])
    route_avg_coupling_table.float_format = .2
    route_avg_coupling_table.align = "c"
    row_contents = [routeAvgCouplingHOP[i] for i in rowSPNames[1:]]
    route_avg_coupling_table.add_row( row_contents )
    print "Routes - Mean Coupling HOP"
    pprint.pprint(routeAvgCouplingHOP)
    output_file.write("<h1>Routes - Mean Coupling HOP Metric</h1>")
    output_file.write(route_avg_coupling_table.get_html_string())


    # Routes - Mean Coupling - FFTT Metric
    route_avg_coupling_table = PrettyTable(rowSPNames[1:])
    route_avg_coupling_table.float_format = .2
    route_avg_coupling_table.align = "c"
    row_contents = [routeAvgCouplingFFTT[i] for i in rowSPNames[1:]]
    route_avg_coupling_table.add_row( row_contents )
    print "Routes - Mean Coupling FFTT"
    pprint.pprint(routeAvgCouplingFFTT)
    output_file.write("<h1>Routes - Mean Coupling FFTT metric</h1>")
    output_file.write(route_avg_coupling_table.get_html_string())

    # Routes - Mean Demand-Weighted Coupling
    route_avg_weighted_coupling_table = PrettyTable(rowSPNames[1:])
    route_avg_weighted_coupling_table.float_format = .2
    route_avg_weighted_coupling_table.align = "c"
    ODweights = ODs.getSP_demands(demands)
    s = float(sum(ODweights))
    row_contents = [routeAvgCouplingHOP[i] for i in rowSPNames[1:]]
    row_contents = [(row_contents[i] * ODweights[i])/s for i in range(len(row_contents))]
    route_avg_weighted_coupling_table.add_row( row_contents )
    print "Routes - Mean Demand-Weighted Coupling"
    pprint.pprint(row_contents)
    output_file.write("<h1>Routes - Mean Demand-Weighted Coupling</h1>")
    output_file.write(route_avg_weighted_coupling_table.get_html_string())


    # Routes - #Agents per Route (from simulation)
    if simulation_results_available==True:
        route_number_agents_at_convergence_table = PrettyTable(SPNames_from_simulation) #xxx
        route_number_agents_at_convergence_table.float_format = .2
        route_number_agents_at_convergence_table.align = "c"
        row_contents = [(100.0*i)/sum(nDriversPerOD) for i in nDriversPerOD] # normalize #drivers in each route by the total #drivers
        #row_contents = [i for i in nDriversPerOD] # normalize #drivers in each route by the total #drivers xxx
        route_number_agents_at_convergence_table.add_row( row_contents )
        print "Routes - #Agents per Route (at convergence, from simulation)"
        pprint.pprint(row_contents)
        output_file.write("<h1>Routes - #Agents per Route</h1>")
        output_file.write("<h4><i>(at convergence, from simulation, normalized)</i></h4>")
        output_file.write(route_number_agents_at_convergence_table.get_html_string())

    output_file.write("<br><hr style=\"height:15px;border:none;color:#333;background-color:#622;\"/>")


    # Mean Link Coupling (Geometric Average of MeanCoupling of Routes where a Link Appears In)
    link_coupling_table = PrettyTable(rowLinkNames[:])
    link_coupling_table.float_format = .2
    link_coupling_table.align = "c"
    linkCoupling = ODs.getLinkCoupling(routeAvgCoupling)
    row_contents = [linkCoupling[i] for i in rowLinkNames[:]]
    link_coupling_table.add_row( row_contents )
    print "Links - Mean Coupling"
    pprint.pprint(linkCoupling)
    output_file.write("<h1>Links - Mean Coupling</h1>")
    output_file.write("<h4><i>(Geometric Average of the Mean Coupling of all Routes where the Link Appears)</i></h4>")
    output_file.write(link_coupling_table.get_html_string())


    # Simulation Link Occupancy results
    if simulation_results_available==True:
        simul_table = PrettyTable(rowLinkNames[:])
        simul_table.float_format = .2
        simul_table.align = "c"
        print "Links - #Agents per Route"
        row_contents = []
        for i in rowLinkNames[:]:
            row_contents.append( nDriversPerLink[i] )
        s = sum(row_contents)
        row_contents = [100*float(i) / s for i in row_contents]
        pprint.pprint(row_contents)
        simul_table.add_row( row_contents )
        output_file.write("<h1>Links - #Agents per Route</h1>")
        output_file.write("<h4><i>(at convergence, from simulation, normalized)</i></h4>")
        output_file.write(simul_table.get_html_string())


    # Link Presence in Routes/Shortest Paths
    link_presence_table = PrettyTable(rowLinkNames[:])
    link_presence_table.float_format = .2
    link_presence_table.align = "c"
    linkPresence = ODs.getPercentageRoutesEachLinkAppearsIn()
    row_contents = [linkPresence[i] for i in rowLinkNames[:]]
    link_presence_table.add_row( row_contents )
    print "Links - Presence(%) in Routes/Shortest Paths"
    pprint.pprint(linkPresence)
    output_file.write("<h1>Links - Presence(%) in Routes/Shortest Paths</h1>")
    output_file.write(link_presence_table.get_html_string())

    print "\n\nOutput table saved in %s" % output_filename
    output_file.write("</center></body></html>")
    output_file.close()
    '''