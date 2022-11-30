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

U = np.linspace(50, 700, 14)

udir = {}
for d in dirs:
    #ui = U[int(d.name.split('.')[1])-1]
    with (d / 'parameters.yaml').open('r') as f:
        pDir = yaml.safe_load(f)
    ui = pDir['U']
    mod = d / 'model-modal-nLinear-restart.mod'
    xlsx = d / 'iteration-F-U.xlsx'
    if mod.is_file():
        copy(mod, destDir / f'{int(ui)}.mod')
        copy(xlsx, destDir / f'{int(ui)}.xlsx')
    file = d / 'results.json'
    if not file.is_file():
        print(f'{d} does not have results.json')
    else:
        with file.open('r') as f:
            udir[file.parent.name]  = json.load(f)
        

#U = [50, 100, 150, 200, 250, 300, 350, 400, 450]
#modesDir = {}
#for i, ui in enumerate(U):
#    modesDir[ui] = udir['run.' + str(i+1)]
#
#fig, ax = plt.subplots()
#for i in range(1,11):
#    mode = [modesDir[ui][f'mode-{i}'] for ui in U]
#    #fig2 , ax2 = plt.subplots()
#    #ax2.plot(U, mode, label=f'mode-{i}')
#    #ax2.legend()
#    #plt.savefig(f'mode-{i}.png', dpi=300)
#    ax.plot(U, mode, label=f'mode-{i}')
#
##ax.legend()
#plt.savefig(f'allModes.png', dpi=300)
    




