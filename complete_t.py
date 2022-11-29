from pyNastran.bdf.bdf import BDF
import pandas as pd
import tables
from pathlib import Path
import numpy as np
import sys
import pickle
from Wing import Wing

def centroid(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:,0])
    sum_y = np.sum(arr[:,1])
    sum_z = np.sum(arr[:,2])
    return sum_x/length, sum_y/length, sum_z/length

if __name__ == '__main__':

    errorMessage='''Usage: python complete.py <analysis>
        analysis: linear, nLinear or modal'''

    if len(sys.argv) != 2:
        print(errorMessage)
        sys.exit(1)


    # BDF
    bdf = BDF()
    bdf.read_bdf('main.bdf')
    wing = Wing(9.0, [4.0, 1.0], 'modelBDF.h5')

    setsRbe3 = wing.getNodesRbe3(tol={{tol}})
    setsAirfoilCG = wing.getNodesRbe3(tol=0.05)
    ids = 5000
    for i, (sR, sA) in enumerate(zip(setsRbe3, setsAirfoilCG)):
        bdf.add_set1(i+1, sR['ID'])
        xyz = centroid(sA['X'])
        bdf.add_grid(5000+i, xyz)
        n = len(sR['ID'])
        bdf.add_rbe3(5000+i, 5000+i, refc = '123456', weights = [1.0]*n, 
                    Gijs = sR['ID'], comps = ['123']*n)
        #bdf.add_rbe2(5000+i, 5000+i, cm = '123456', Gmi = s['ID'])

    D = np.loadtxt('load_Uy.mat')
    L = np.loadtxt('load_Uz.mat')
    M = np.loadtxt('load_Um.mat')

    # Avoid Nastran error if any loads is zero
    D[D==0] = 1e-4
    L[L==0] = 1e-4
    M[M==0] = 1e-4

    #set2 = bdf.subcases[0]['SET 2'][0]
    set2 = [5000+i for i in range(len(setsRbe3))]
    coords = [bdf.nodes[nid].xyz for nid in set2]  
    wing.addSet(2, set2, coords)

    for node, (Di, Li, Mi) in zip(set2, zip(D,L,M)):
        bdf.add_force(1, node, 1.0, (Di, 0.0, 0.0))
        bdf.add_force(1, node, 1.0, (0.0, 0.0, Li))
        bdf.add_moment(1, node, 1.0, (0.0, Mi, 0.0))

    bdf.add_grav(2, 1.0, [0.0, 0.0, -1.0])
    bdf.add_load(3, 1.0, [{{aeroFactor}}, {{gravFactor}}], [1, 2])

    if sys.argv[1] == 'nLinear':
        bdf.sol = 400
        bdf.write_bdf('model-nLinear.bdf')
    elif sys.argv[1] == 'linear':
        bdf.sol = 101
        sub = bdf.subcases[1]
        del sub.params['']
        bdf.write_bdf('model-linear.bdf')
    elif sys.argv[1] == 'modal':
        bdf.sol = 103
        sub = bdf.subcases[1]
        del sub.params['']
        bdf.write_bdf('model-modal.bdf')
    else:
        print(errorMessage)
        sys.exit(1)

    with open('wing.obj', 'wb') as f:
        pickle.dump(wing, f)


