from pyNastran.bdf.bdf import BDF
import pandas as pd
import tables
from pathlib import Path
from scipy.io import savemat
import numpy as np
import sys
import pickle
# Import class for pickling
from Wing import Wing

cwd = Path.cwd()

errorMessage='''Usage: python post.py <analysis>
       analysis: linear, nLinear or modal'''
if len(sys.argv) != 2:
    print(errorMessage)
    exit(1)
analysis = sys.argv[1]

with open('wing.obj', 'rb') as f:
    wing = pickle.load(f)

# HDF5
h5file = tables.open_file(f'model-{analysis}.h5', 'r')
disph5 = h5file.root.NASTRAN.RESULT.NODAL.DISPLACEMENT

# Get Domain ID for last iteration
dId = max(disph5.read()['DOMAIN_ID'])
queryString = '(ID == 5000)'
for i in range(1,len(wing.yPos[1:])):
    queryString = queryString + f' | (ID == {5000+i})'
queryString = f"(DOMAIN_ID == {dId}) & ({queryString})"

angles = []
for row in disph5.where(queryString):
    angles.append(row['RY'])

angles = -np.degrees(angles)
mdict = {'RY': angles}
savemat('RY.mat', mdict)
np.savetxt('RY.txt', angles)


h5file.close()
