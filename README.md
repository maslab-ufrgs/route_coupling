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

## Output

the output will be in the form of a csv file in the folder from which the code
was ran.
