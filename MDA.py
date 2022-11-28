from subprocess import run, PIPE, CalledProcessError
from pathlib import Path
import numpy as np
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from Wing import Wing
from time import time
from config import octave, nastran

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
octave[0] = octave[0] + ' ' + matScript.name + ' ' + '1'
octaveInit = run(octave, shell=True, stdout = PIPE)

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

def divergeExit(message):
    print(message)
    print('Diverged!!')
    results = CWD / 'results.json'
    with resultsFileFinal.open('w') as f:
        json.dump({'mode:' 'Diverged'}, f)
    sys.exit(1)


while not np.allclose(ryHistory[-2], ryHistory[-1], atol=1e-3):
    print(f'Iteration {len(ryHistory)}')
    start = time()
    try:
        status = run([f"doit -a loads analysis={analysis}"], shell=True, check=True)
    except CalledProcessError:
        divergeExit('Analysis did not converged')
    end = time()
    print(f'Elapsed time = {end-start}s')
    ry = np.loadtxt('RY.txt')
    print('Angles: ')
    print(ry)
    ryHistory.append(ry)
    if np.any(ry > 6.0):
        divergeExit('Angles values too high')


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
    nastran_restart = 'model-nLinear-modal-restart.bdf'
    status = run(nastran + [nastran_restart,], shell=True)
    statusMod = run(["python",  "processModes.py", nastran_restart], shell=True)

