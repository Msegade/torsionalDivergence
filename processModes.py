from pyNastran.bdf.bdf import BDF
import pandas as pd
import tables
import sys
from pathlib import Path
from Wing import Wing
import pickle
import numpy as np
import json

def getEigVectArray(eigenvector, setS, mode):
    eigvalues = []
    for node in setS:
        eigv = eigenvector[(eigenvector['ID'] == node) & \
                           (eigenvector['DOMAIN_ID'] == mode)]
        eigvalues.append(eigv[['X','Y','Z','RX','RY','RZ']].tolist()[0])
    return eigvalues

def getDataFrameForMode(eigenvector, wing, mode):

    setS =  wing.setDict[2]['ids']
    yPos = wing.yPos[1:]
    chords = wing.chords
    eigvalues = getEigVectArray(eigenvector, setS, mode)
    df1 = pd.DataFrame(zip(yPos, chords), index=setS, 
                    columns=['Y-Pos', 'Chord'])
    df2 = pd.DataFrame(eigvalues, index=setS,
                    columns=['x', 'y', 'z', 'rx', 'ry','rz'])
    df = pd.concat([df1, df2], axis=1)
    return df

CWD = Path.cwd()
wingObj = CWD / 'wing.obj'

with wingObj.open('rb') as f:
    wing = pickle.load(f)

bdfFileName = sys.argv[1]
bdf = CWD / bdfFileName

# HDF5
hdf5FileName = bdf.with_suffix('.h5')
h5file = tables.open_file(hdf5FileName, 'r')
eigenvector = h5file.root.NASTRAN.RESULT.NODAL.EIGENVECTOR.read()
eigenvalues = h5file.root.NASTRAN.RESULT.SUMMARY.EIGENVALUE.read()

dfs = []
modes = eigenvalues['FREQ']

xlsx = bdf.with_suffix('.xlsx')
writer = pd.ExcelWriter(xlsx, engine='xlsxwriter')

n0 = min(eigenvector['DOMAIN_ID'])
for i, mode in enumerate(modes):
    # Start at first domain_id
    n = n0+i
    df = getDataFrameForMode(eigenvector, wing, n)
    df.to_excel(writer, sheet_name=f'Freq = {mode}')
    dfs.append(df)

mod = bdf.with_suffix('.mod')
file = mod.open('w')
for i, (df, mode)  in enumerate(zip(dfs, modes)):
    n = i+1
    # In hertz
    file.write(f'{n} {mode*2*np.pi} \n')
    for j, row in enumerate(df.iterrows()):
        ev = row[1]
        lineEv = f'{ev.x} {ev.y} {ev.z} {ev.rx} {ev.ry} {ev.rz}'
        file.write(f'{j+1} {lineEv} \n')

results = CWD / 'results.json'
with results.open('w') as f:
    json.dump({'mode': modes[0]}, f)

file.close()
h5file.close()
writer.save()
