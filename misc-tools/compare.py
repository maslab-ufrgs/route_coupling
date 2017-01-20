fernando = open("routes.fernando")
thiago = open("routes.thiago")

routesfernando = [x.replace("\n", "") for x in fernando.readlines()]

routesthiago = [x.replace("\n", "") for x in thiago.readlines()]

routesfernando = sorted(routesfernando)
routesthiago = sorted(routesthiago)

for i in range(len(routesfernando)):
	if(routesfernando[i] != routesthiago[i]):
		print routesfernando[i], routesthiago[i],"error"
		break
