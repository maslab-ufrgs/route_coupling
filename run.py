files = ['Berlin-Friedrichshain.net.routes.k8',
	'Berlin-Mitte-Center.net.routes.k8',
	'Berlin-Mitte-Prenzlauerberg-Friedrichshain-Center.net.routes.k8',
	'Berlin-Prenzlauerberg-Center.net.routes.k8',
	'OW.net.routes.k5',
	'OW.net.routes.k8',
	'SiouxFalls.net.routes.k8']

k = 8 

import os
for filename in files:
	os.system("python coupling2.py routefiles/%s %d" % (filename, k))

