from pyNastran.bdf.bdf import BDF
import pandas as pd
import tables
from pathlib import Path
from scipy.io import savemat, loadmat
import numpy as np
import sys
import pickle
# Import class for pickling
from Wing import Wing

CWD = Path.cwd()

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

def addToDict(iterDict, row):
    dispDict = {}
    for label in ['X', 'Y', 'Z', 'RX', 'RY', 'RZ']:
        dispDict[label] = row[label]
    iterDict[row['ID']] = dispDict

angles = []
iterDict = {}
for row in disph5.where(queryString):
    print(row['ID'])
    angles.append(row['RY'])
    addToDict(iterDict, row)
    
M = np.loadtxt('load_Um.mat')
L = np.loadtxt('load_Uz.mat')
D = np.loadtxt('load_Uy.mat')
for i, (Mi, Li, Di) in enumerate(zip(M,L,D)):
    iterDict[5000+i]['M'] = Mi
    iterDict[5000+i]['L'] = Li
    iterDict[5000+i]['D'] = Di

df = pd.DataFrame(iterDict)
iterationFile = CWD / 'iteration-F-U.xlsx'
if iterationFile.is_file():
    xlsx = pd.ExcelFile(iterationFile)
    nSheets = len(xlsx.sheet_names)
    with pd.ExcelWriter(iterationFile, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name=f'Iteration-{nSheets+1}')
else:
    df.to_excel(iterationFile, sheet_name=f'Iteration-1')
    
angles = -np.degrees(angles)
mdict = {'RY': angles}
savemat('RY.mat', mdict)
np.savetxt('RY.txt', angles)

h5file.close()
