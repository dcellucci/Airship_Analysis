import pickle

nodes = []
struts = []
forces = []

filename = "psch_airship"

with open(filename+".nodes", 'r') as inf:
    for infline in inf.readlines():
        nodes.append([float(a)/1000.0 for a in infline[1:-2].split(",")])
        #divide by 1000 to get coordinates in meters

with open(filename+".struts",'r') as inf:
    for infline in inf.readlines():
        struts.append([int(round(float(a))) for a in infline[1:-2].split(",")][0:2])

with open(filename+"_load.forces",'r') as inf:
    inflines = inf.readlines()
    for i in range(0,len(inflines)-1,2):
        forcevect = [float(a) for a in inflines[i][1:-2].split(",")]
        forces.append((int(round(float(inflines[i+1]))),forcevect))

with open(filename+"_lift.forces",'r') as inf:
    inflines = inf.readlines()
    for i in range(0,len(inflines)-1,2):
        forcevect = [float(a) for a in inflines[i][1:-2].split(",")]
        forces.append((int(round(float(inflines[i+1]))),forcevect))

print forces
rawdata = {}
rawdata["nodes"] = nodes
rawdata["struts"] = struts
rawdata["forces"] = forces
with open(filename+"_rawdata.pickle", 'wb') as outf:
    pickle.dump(rawdata,outf,pickle.HIGHEST_PROTOCOL)
