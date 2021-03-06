#import matplotlib.pyplot as plt
#import matplotlib
#from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import subprocess
import pfea
import cProfile
import pfea.frame3dd
import pfea.solver
from pfea.util import pfeautil
from math import *
import pickle



filenames = ["psch_airship_b","shell_airship"]
foldernames = ["psch_airship_b","shell_airship"]
node_lifts = [33,40] #N, per node


index = 0
# Reading rawdata file
path = 'raw/{0}/{1}_rawdata.pickle'.format(foldernames[index], filenames[index])
with open(path, 'rb') as f:
    pa_rawdata = pickle.load(f)

# Material Properties

nodes = np.array(pa_rawdata["nodes"])
frames = np.array(pa_rawdata["struts"])
lift_forces = pa_rawdata["lift_forces"]
load_frames = pa_rawdata["load_struts"]

#Physical Voxel Properties
node_radius = 0

#STRUT PROPERTIES
#Physical Properties
#A pultruded carbon fiber 5mm OD 3mm ID tube
#Using Newtons, meters, and kilograms as the units
frame_props = {"nu"  : 0.3, #poisson's ratio
			   "d1"	 : 0.0624, #m
			   "th"	 : 0.0312, #m
			   "E"   :  1e7, #N/m^2
               'yield_strength':117e6 ,#N/m^2
			   "rho" :  18.579, #kg/m^3
               "node_mass": 0.015, #kg
			   "beam_divisions" : 10,
			   "cross_section"  : 'circular',
			   "roll": 0,
			   "Le":0.88}

lframe_props = {"nu"  : 0.3, #poisson's ratio
			   "d1"	 : 0.0624, #m
			   "th"	 : 0.0312, #m
               'yield_strength':117e6 ,#N/m^2
			   "E"   :  1e8, #N/m^2
			   "rho" :  2, #kg/m^3
               "node_mass": 0.015, #kg
			   "beam_divisions" : 10,
			   "cross_section"  : 'circular',
			   "roll": 0,
			   "Le":10}

#Node Map Population
#Referencing the geometry-specific cuboct.py file.


#Constraint and load population
constraints = []
loads = []

daniel = 80*9.8 #N

##
## Adding Loads to the structure
##
node_lift = node_lifts[index]
#print("Lift Load: {0} N".format(factor))
for load in lift_forces:
    for c in range(3):
        loads.append({'node':load[0],'DOF':c, 'value':load[1][c]*node_lift})


#print loads
for nodeid in pa_rawdata["constraints"]:
    constraints.append({'node':nodeid, 'DOF':0, 'value':0})
    constraints.append({'node':nodeid, 'DOF':1, 'value':0})
    constraints.append({'node':nodeid, 'DOF':2, 'value':0})
    #constraints.append({'node':nodeid, 'DOF':3, 'value':0})
    #constraints.append({'node':nodeid, 'DOF':4, 'value':0})
    #constraints.append({'node':nodeid, 'DOF':5, 'value':0})

#constraints.append({'node':127, 'DOF':0, 'value':0})
#constraints.append({'node':127, 'DOF':1, 'value':0})

#print(len(loads))

 #####  ### #     #    ####### #     # ####### ######  #     # #######
#     #  #  ##   ##    #     # #     #    #    #     # #     #    #
#        #  # # # #    #     # #     #    #    #     # #     #    #
 #####   #  #  #  #    #     # #     #    #    ######  #     #    #
      #  #  #     #    #     # #     #    #    #       #     #    #
#     #  #  #     #    #     # #     #    #    #       #     #    #
 #####  ### #     #    #######  #####     #    #        #####     #

#Format node positions
out_nodes = np.array(nodes)

#Group frames with their characteristic properties.
out_frames = [(np.array(frames),[],{'E'   : frame_props["E"],
								 'yield_strength': frame_props["yield_strength"],
								 'rho' : frame_props["rho"],
								 'nu'  : frame_props["nu"],
								 'd1'  : frame_props["d1"],
								 'th'  : frame_props["th"],
								 'beam_divisions' : frame_props["beam_divisions"],
								 'cross_section'  : frame_props["cross_section"],
								 'roll': frame_props["roll"],
                                 'node_mass':frame_props["node_mass"],
                                 'loads':{'element':0},
								 'prestresses':{'element':0},
								 'Le': frame_props["Le"]})]
for lframe in load_frames:
    #lframe_props = copy(lframe_props)
    out_frames.append((np.array([lframe]),[],{'E'   : lframe_props["E"],
    								 'yield_strength': lframe_props["yield_strength"],
    								 'rho' : lframe_props["rho"],
    								 'nu'  : lframe_props["nu"],
    								 'd1'  : lframe_props["d1"],
    								 'th'  : lframe_props["th"],
    								 'beam_divisions' : lframe_props["beam_divisions"],
    								 'cross_section'  : lframe_props["cross_section"],
    								 'roll': lframe_props["roll"],
                                     'node_mass':lframe_props["node_mass"],
                                     'loads':{'element':0},
    								 'prestresses':{'element':0},
    								 'Le': np.linalg.norm(out_nodes[lframe[0]]-out_nodes[lframe[1]])}))


out_nodes, out_frames = pfeautil.subdivide_Frames(out_nodes,out_frames)

#Global Arguments
global_args = {'frame3dd_filename': "br_s_mt", 'length_scaling':1,"using_Frame3dd":False,"output_file":True,"debug_plot":False, "gravity" : [0,0,-9.8]}

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
if global_args["output_file"]:
    folder = "."
    filename = filenames[index]
    sim = {}
    sim["nodes"] = out_nodes
    sim["frames"] = out_frames
    sim["displacements"] = res_displace
    sim["Q"] = Q
    sim["loads"] = loads
    sim["constraints"] = constraints
    with open(folder+"/"+filename+"_simresults.pickle", 'wb') as outf:
        pickle.dump(sim,outf,pickle.HIGHEST_PROTOCOL)

if global_args["debug_plot"]:
    import pfea.util.debugplot_pyqtgraph as dbp
    dbp.debugplot(out_nodes,out_frames,res_displace,Q,loads,constraints,1, axial_forces=True)
