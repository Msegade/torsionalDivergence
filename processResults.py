import pandas as pd
import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt
from shutil import copy
import sys
import yaml

cwd = Path.cwd()
baseDir = cwd / sys.argv[1]

dirs = baseDir.glob('run*')
destDir = baseDir / 'results'
destDir.mkdir(exist_ok=True)

def getZRyLastIteration(xlsx, node=5009):

    xlsx = pd.ExcelFile(xlsx)
    nSheets = len(xlsx.sheet_names)

    df = pd.read_excel(xlsx, sheet_name=f'Iteration-{nSheets}')
    df.set_index('Unnamed: 0', inplace=True)
    RY = df[node].RY
    Z = df[node].Z
    return Z, RY

modesDir = {}
Uconv = []
Zs = []
RYs = []
for d in dirs:
    #ui = U[int(d.name.split('.')[1])-1]
    with (d / 'parameters.yaml').open('r') as f:
        pDir = yaml.safe_load(f)
    ui = pDir['U']
    mod = d / 'model-modal-nLinear-restart.mod'
    xlsx = d / 'iteration-F-U.xlsx'
    # Check if converged
    if not mod.is_file():
        continue
    Uconv.append(ui)
    copy(mod, destDir / f'{int(ui)}.mod')
    copy(xlsx, destDir / f'{int(ui)}.xlsx')
    Z, RY = getZRyLastIteration(xlsx)
    Zs.append(Z)
    RYs.append(RY)
    file = d / 'results.json'
    if not file.is_file():
        print(f'{d} does not have results.json')
    else:
        with file.open('r') as f:
            modesDir[ui] = json.load(f)          

# Sort arrays based on U        
U = np.sort(Uconv)
idx = np.argsort(Uconv)
Zs = np.array(Zs)
RYs = np.degrees(RYs)
Zs = Zs[idx]
RYs = RYs[idx]

nModes = len(modesDir[U[0]].keys())
nModes = 9

fig, ax = plt.subplots()
for i in range(1,nModes+1):
    mode = [modesDir[ui][f'mode-{i}'] for ui in U]
    fig2 , ax2 = plt.subplots()
    ax2.plot(U, mode, label=f'mode-{i}')
    ax2.legend()
    plt.savefig(destDir / f'mode-{i}.png', dpi=300)
    plt.close(fig2)
    ax.plot(U, mode, label=f'mode-{i}')

#ax.legend()
plt.savefig(destDir / f'allModes.png', dpi=300)
plt.close(fig)


fig, ax = plt.subplots()
ax.plot(U, Zs, label='Z')
ax.set_ylabel('Vertical Displacement')
ax.legend()
ax2 = ax.twinx()
ax2.plot(U, RYs, label='RY', color='r')
ax2.set_ylabel('Tip Angle')
ax2.legend()
plt.savefig(destDir / 'U-ZRY.png', dpi=300)




