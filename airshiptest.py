import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import subprocess
import pfea
import cProfile
import pfea.frame3dd
import pfea.solver
from math import *
import pickle

# Reading rawdata file
with open('raw/psch_airship_rawdata.pickle', 'rb') as f:
    pa_rawdata = pickle.load(f)

# Material Properties

nodes = np.array(pa_rawdata["nodes"])
frames = np.array(pa_rawdata["struts"])
forces = pa_rawdata["forces"]


#Physical Voxel Properties
node_radius = 0

#STRUT PROPERTIES
#Physical Properties
#A pultruded carbon fiber 5mm OD 3mm ID tube
#Using Newtons, meters, and kilograms as the units
frame_props = {"nu"  : 0.3, #poisson's ratio
			   "d1"	 : 0.0624, #m
			   "th"	 : 0.0312, #m
			   "E"   :  0.5e7, #N/m^2
			   "rho" :  1600, #kg/m^3
			   "beam_divisions" : 0,
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

for load in forces:
	for c in range(3):
		loads.append({'node':load[0],'DOF':c, 'value':load[1][c]*total_load})

constraintids = [404,416,426,438]

constraints.append({'node':404, 'DOF':0, 'value':0})
constraints.append({'node':404, 'DOF':1, 'value':0})
constraints.append({'node':404, 'DOF':2, 'value':0})
constraints.append({'node':404, 'DOF':3, 'value':0})
constraints.append({'node':404, 'DOF':4, 'value':0})
constraints.append({'node':404, 'DOF':5, 'value':0})
constraints.append({'node':416, 'DOF':2, 'value':0})
constraints.append({'node':426, 'DOF':2, 'value':0})
constraints.append({'node':438, 'DOF':2, 'value':0})



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
	#print "skipping fea for now"
	res_displace,C,Q = pfea.solver.analyze_System(out_nodes, global_args, out_frames, constraints,loads)


Q = np.array(Q)

######  ####### ######  #     #  #####
#     # #       #     # #     # #     #
#     # #       #     # #     # #
#     # #####   ######  #     # #  ####
#     # #       #     # #     # #     #
#     # #       #     # #     # #     #
######  ####### ######   #####   #####

if global_args["debug_plot"]:
	### Right now the debug plot only does x-y-z displacements, no twisting
	xs = []
	ys = []
	zs = []

	rxs = []
	rys = []
	rzs = []

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.set_aspect('equal')
	frame_coords = []
	factor = 1

	#print(matplotlib.projections.get_projection_names())
	for i,node in enumerate(nodes):
		xs.append(node[0])
		ys.append(node[1])
		zs.append(node[2])
		rxs.append(node[0]+res_displace[i][0]*factor)
		rys.append(node[1]+res_displace[i][1]*factor)
		rzs.append(node[2]+res_displace[i][2]*factor)

	frame_args = out_frames[0][2]
	st_nrg = 0.5*frame_args["Le"]/frame_args["E"]*(Q.T[0]**2/frame_args["Ax"]+Q.T[4]**2/frame_args["Iy"]+Q.T[5]**2/frame_args["Iz"])
	qmax = np.max(st_nrg)


	print("Maximum Energy: {0}".format(qmax))
	for i,frame in enumerate(frames):
		nid1 = int(frame[0])
		nid2 = int(frame[1])
		start = [xs[nid1],ys[nid1],zs[nid1]]
		end   = [xs[nid2],ys[nid2],zs[nid2]]
		rstart = [rxs[nid1],rys[nid1],rzs[nid1]]
		rend   = [rxs[nid2],rys[nid2],rzs[nid2]]

		ax.plot([start[0],end[0]],[start[1],end[1]],[start[2],end[2]],color='r', alpha=0.1)
		ax.plot([rstart[0],rend[0]],[rstart[1],rend[1]],[rstart[2],rend[2]],color='b', alpha=(1.0*st_nrg[i]/qmax)**2)
	'''
	for dframe in dframes:
		nid1 = int(dframe[0])
		nid2 = int(dframe[1])
		dstart = [dxs[nid1],rys[nid1],rzs[nid1]]
		dend   = [dxs[nid2],rys[nid2],rzs[nid2]]
		ax.plot([dstart[0],dend[0]],[dstart[1],dend[1]],[dstart[2],dend[2]],color='b', alpha=0.1)
	'''

	ax.scatter(xs,ys,zs, color='r',alpha=0.1)
	ax.scatter(rxs,rys,rzs, color='b',alpha=0.3)
	plt.show()
	#print(frames)
