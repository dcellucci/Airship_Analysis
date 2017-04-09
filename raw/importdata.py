import pickle

nodes = []
struts = []
lift_forces = []
load_struts = []
constraints = []

folder = "psch_airship_b"#"shell_airship"
filename = "psch_airship_b"#"shell_airship"

with open(folder+"/"+filename+".nodes", 'r') as inf:
    for infline in inf.readlines():
        nodes.append([float(a)/1000.0 for a in infline[1:-2].split(",")])
        #divide by 1000 to get coordinates in meters

with open(folder+"/"+filename+".struts",'r') as inf:
    for infline in inf.readlines():
        struts.append([int(round(float(a))) for a in infline[1:-2].split(",")][0:2])

with open(folder+"/"+filename+"_load.struts",'r') as inf:
    for infline in inf.readlines():
        load_struts.append([int(round(float(a))) for a in infline[1:-2].split(",")][0:2])

with open(folder+"/"+filename+"_lift.forces",'r') as inf:
    inflines = inf.readlines()
    for i in range(0,len(inflines)-1,2):
        forcevect = [float(a) for a in inflines[i][1:-2].split(",")]
        lift_forces.append((int(round(float(inflines[i+1]))),forcevect))

with open(folder+"/"+filename+".constraints",'r') as inf:
    for infline in inf.readlines():
        constraints.append(int(infline))

print constraints
rawdata = {}
rawdata["nodes"] = nodes
rawdata["struts"] = struts
rawdata["load_struts"] = load_struts
rawdata["lift_forces"] = lift_forces
rawdata["constraints"] = constraints
with open(folder+"/"+filename+"_rawdata.pickle", 'wb') as outf:
    pickle.dump(rawdata,outf,pickle.HIGHEST_PROTOCOL)
