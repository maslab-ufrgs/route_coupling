#!/bin/bash
networks = ("Berlin-Friedrichshain.net" "Berlin-Mitte-Center.net" "Berlin-Mitte-Prenzlauerberg-Friedrichshain-Center.net" "Berlin-Prenzlauerberg-Center.net" "OW.net" "SiouxFalls.net")


for n in "${networks[@]}"
do
	echo "----------------------------\n"
	echo "generating route file for $n\n"
	time python calculateRoutes.py "networks/$n" 8 "routefiles/$n.routes.k8"
	echo "calculating coupling for $n\n"
	time python coupling2.py "routefiles/$n.routes.k8" 8 
done


