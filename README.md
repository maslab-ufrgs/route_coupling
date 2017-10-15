Route coupling
====================================
This script calculates the coupling of routes in a instance of the route
choice problem.


## Requirements
There is the need to initialize the submodules, to do so use the following command:
```sh
git submodule init && git submodule update
```

## Usage
to calculate the coupling, use the couplin2.py script
it has the following parameters:

-nf: the network file

-rf: the route file
(one of these two must be provided. if both are, the route file will be used)

-sf: the simulation output file

-k: parameter for ksp

example:

python coupling2.py -nf networks/OW.net -k 8

## Route Files
Instead of calculating the routes at each execution, one can pre-process
a network file with the goal of generating a route file. To do this simply
execute the command below. K is the number of routes to calculate for each OD
pair.

```
calculateRoutes.py inputnet k outputfile
```

## Output

the output will be in the form of a csv file in the folder from which the code
was ran.

The outuput format is as follows:
```
Route CouplingHop CouplingFFTT
10|1(1) 2.60478332939 2.56208196333
```
CouplingHop indicates the non-weighted coupling metric. i.e. all edges
have the same weigth.

CouplingFFTT indicates the weighted coupling metric using the free flow travel
time of each edge as its weight.
