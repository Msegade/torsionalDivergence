from subprocess import run, PIPE
from pathlib import Path
import numpy as np
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from Wing import Wing
from time import time

CWD = Path.cwd()
matScript = CWD / 'loads.m'

errorMessage='''Usage: python MDA <analysis>
    analysis: linear or nLinear'''

if len(sys.argv) != 2:
    print(errorMessage)
    sys.exit(1)

analysis=sys.argv[1]

# First load values
print('Getting initial load vector')
doitInit = run(["doit run init:loads.m"], shell=True, stdout = PIPE)
octaveInit = run(['octave', matScript, '1'], stdout = PIPE)

ryHistory = []

# First iteration
print('Iteration 1')
status = run([f"doit run -a loads analysis={analysis}"], shell=True, check=True)
ry = np.loadtxt('RY.txt')
print('Angles: ')
print(ry)
ryInit = [0.0]*len(ry)
ryHistory.append(ryInit)
ryHistory.append(ry)

while not np.allclose(ryHistory[-2], ryHistory[-1], atol=1e-3):
    print(f'Iteration {len(ryHistory)}')
    start = time()
    status = run([f"doit -a loads analysis={analysis}"], shell=True, check=True)
    end = time()
    print(f'Elapsed time = {end-start}s')
    ry = np.loadtxt('RY.txt')
    print('Angles: ')
    print(ry)
    ryHistory.append(ry)

with open('wing.obj', 'rb') as f:
    wing = pickle.load(f)

ryDict = {f'Iteration-{i+1}': ry  for i, ry in enumerate(ryHistory)}
ryDict['yPos'] = wing.yPos[1:]
df = pd.DataFrame(ryDict)
df.set_index('yPos', inplace=True)
df.to_csv(f'ryHistory-{analysis}.csv')
sns.lineplot(data=df)
plt.savefig('Graph.png', dpi=300)

# Modal analysis
if analysis == 'nLinear':
    nastran = '/opt/nastran/2019/bin/nast20191'
    nastran_opts = ['old=no', 'batch=no', 'mem=1GB', 'scratch=yes', 'append=yes']
    nastran_restart = 'model-nLinear-modal-restart.bdf'
    status = run([[nastran,]+nastran_opts+[nastran_restart,]], shell=True)
    statusMod = run(['python processModes.py model-nLinear-modal-restart.bdf'])

