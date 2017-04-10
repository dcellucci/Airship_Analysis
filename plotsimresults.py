import pfea.util.debugplot_pyqtgraph as dbp
import pickle

filenames = ["psch_airship_b","shell_airship"]
foldernames = ["psch_airship_b","shell_airship"]

index = 1

path = '{0}_simresults.pickle'.format(filenames[index])

with open(path, 'rb') as f:
    pa_simresults = pickle.load(f)

out_nodes = pa_simresults["nodes"]
out_frames = pa_simresults["frames"]
res_displace = pa_simresults["displacements"]
Q = pa_simresults["Q"]
loads = pa_simresults["loads"]
constraints = pa_simresults["constraints"]

dbp.debugplot(out_nodes,out_frames,res_displace,Q,loads,constraints,1, axial_forces=True)
