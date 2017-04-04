#import matplotlib.pyplot as plt
#import matplotlib
#from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import subprocess
import pfea
import cProfile
import pfea.frame3dd
import pfea.solver
from math import *
import pickle



# Reading rawdata file
with open('raw/shell_airship/shell_airship_rawdata.pickle', 'rb') as f:
    pa_rawdata = pickle.load(f)

# Material Properties

nodes = np.array(pa_rawdata["nodes"])
frames = np.array(pa_rawdata["struts"])
lift_forces = pa_rawdata["lift_forces"]
load_forces = pa_rawdata["load_forces"]

#Physical Voxel Properties
node_radius = 0

#STRUT PROPERTIES
#Physical Properties
#A pultruded carbon fiber 5mm OD 3mm ID tube
#Using Newtons, meters, and kilograms as the units
frame_props = {"nu"  : 0.3, #poisson's ratio
			   "d1"	 : 0.0624, #m
			   "th"	 : 0.0312, #m
			   "E"   :  5e7, #N/m^2
			   "rho" :  1600, #kg/m^3
			   "beam_divisions" : 1,
			   "cross_section"  : 'circular',
			   "roll": 0,
			   "Le":0.88}

#Node Map Population
#Referencing the geometry-specific cuboct.py file.


#Constraint and load population
constraints = []
loads = []

daniel = 80*9.8 #N
total_load = 14 #N, per node

##
## Adding Loads to the structure
##

factor = 14
print("Lift Load: {0} N".format(factor))
for load in lift_forces:
    for c in range(3):
        loads.append({'node':load[0],'DOF':c, 'value':load[1][c]*factor})


factor = 14
print("Lift Load: {0} N".format(factor))
for load in load_forces:
    for c in range(3):
        loads.append({'node':load[0],'DOF':c, 'value':load[1][c]*factor})

#print loads
for nodeid in pa_rawdata["constraints"]:
    #constraints.append({'node':nodeid, 'DOF':0, 'value':0})
    #constraints.append({'node':nodeid, 'DOF':1, 'value':0})
    constraints.append({'node':nodeid, 'DOF':2, 'value':0})
    #constraints.append({'node':nodeid, 'DOF':3, 'value':0})
    #constraints.append({'node':nodeid, 'DOF':4, 'value':0})
    #constraints.append({'node':nodeid, 'DOF':5, 'value':0})

constraints.append({'node':127, 'DOF':0, 'value':0})
constraints.append({'node':127, 'DOF':1, 'value':0})

#print(len(loads))

 #####  ### #     #    ####### #     # ####### ######  #     # #######
#     #  #  ##   ##    #     # #     #    #    #     # #     #    #
#        #  # # # #    #     # #     #    #    #     # #     #    #
 #####   #  #  #  #    #     # #     #    #    ######  #     #    #
      #  #  #     #    #     # #     #    #    #       #     #    #
#     #  #  #     #    #     # #     #    #    #       #     #    #
 #####  ### #     #    #######  #####     #    #        #####     #



#Group frames with their characteristic properties.
out_frames = [(np.array(frames),[],{'E'   : frame_props["E"],
								 'rho' : frame_props["rho"],
								 'nu'  : frame_props["nu"],
								 'd1'  : frame_props["d1"],
								 'th'  : frame_props["th"],
								 'beam_divisions' : frame_props["beam_divisions"],
								 'cross_section'  : frame_props["cross_section"],
								 'roll': frame_props["roll"],
								 'loads':{'element':0},
								 'prestresses':{'element':0},
								 'Le': frame_props["Le"]})]

#Format node positions
out_nodes = np.array(nodes)

#Global Arguments
global_args = {'frame3dd_filename': "br_s_mt", 'length_scaling':1,"using_Frame3dd":False,"debug_plot":True, "gravity" : [0,0,0]}

if global_args["using_Frame3dd"]:
	frame3dd.write_frame3dd_file(out_nodes, global_args, out_frames, constraints,loads)
	subprocess.call("frame3dd {0}.csv {0}.out".format(global_args["frame3dd_filename"]), shell=True)
	res_nodes, res_reactions = frame3dd.read_frame3dd_results(global_args["frame3dd_filename"])
	res_displace = frame3dd.read_frame3dd_displacements(global_args["frame3dd_filename"])
else:
    res_displace,C,Q = pfea.solver.analyze_System(out_nodes, global_args, out_frames, constraints,loads)

#Q = np.array(Q)

######  ####### ######  #     #  #####
#     # #       #     # #     # #     #
#     # #       #     # #     # #
#     # #####   ######  #     # #  ####
#     # #       #     # #     # #     #
#     # #       #     # #     # #     #
######  ####### ######   #####   #####

if global_args["debug_plot"]:
    import pfea.util.debugplot_pyqtgraph as dbp
    dbp.debugplot(nodes,out_frames,res_displace,Q,loads,constraints,5)
