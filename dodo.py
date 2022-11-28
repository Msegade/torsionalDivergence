from pathlib import Path
from doit import get_var
from itertools import product
import yaml
import re
from jinja2 import Environment, FileSystemLoader
from config import octave, nastran

loader = yaml.SafeLoader
loader.add_implicit_resolver(
    u'tag:yaml.org,2002:float',
    re.compile(u'''^(?:
     [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
    |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
    |\\.[0-9_]+(?:[eE][-+][0-9]+)?
    |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
    |[-+]?\\.(?:inf|Inf|INF)
    |\\.(?:nan|NaN|NAN))$''', re.X),
    list(u'-+0123456789.'))

def prepro(paramFile, templateFile, resultFile):

    with paramFile.open('r') as stream:
        try:
            d = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)            
    
    for key in d:
        if type(d[key]) == str:
            d[key]="'%s'" % d[key]
    
    templateParent = str(templateFile.parent)
    env = Environment(loader=FileSystemLoader(templateParent))
    template = env.get_template(templateFile.name)
    render = template.render(d)

    with resultFile.open('w') as f:
        f.write(render)

def task_init():
    "Generate files from templates using prepro"

    base_path = CWD
    template_files = base_path.glob('*_t.*')
    params_file = base_path / 'parameters.yaml'

    for template in template_files:

        target_name = re.sub('_t', '', template.name)
        targetFile = template.parent / target_name
        targets = [targetFile]
        file_dep = [template, params_file]

        yield {
                'name': target_name,
                'targets': targets,
                'file_dep': file_dep,
                'actions': [(prepro, [params_file, template, targetFile])],
                'clean': True
        }

CWD = Path.cwd()
analysis = get_var('analysis', 'linear')

def task_model():

    script = CWD / 'complete.py'
    bdf = CWD / f'model-{analysis}.bdf'
    wingObj = CWD / 'wing.obj'
    return {
            'targets': [bdf, wingObj],
            'file_dep': ['main.bdf', script, 'modelBDF.h5'],
            'actions': [['python', script, analysis]],
            'clean': True
            }

def task_nastran():

    bdf = CWD / f'model-{analysis}.bdf'
    suffixes = ['.op2', '.h5', '.out', '.IFPDAT', '.MASTER', '.DBALL']
    if analysis == 'nLinear':
        suffixes.append('.sts')
    return {
            'targets': [bdf.with_suffix(suff) for suff in suffixes],
            'file_dep': [bdf,],
            'actions': [nastran +  [bdf,]],
            'clean': True
            }
            
def task_post():

    h5 = CWD / f'model-{analysis}.h5'
    wingObj = CWD / 'wing.obj'

    if analysis == 'linear':
        script = CWD / 'post.py'
        anglesTxt = CWD / 'RY.txt'
        angles = CWD / 'RY.mat'
        ryHistory = CWD / 'ryHistory.txt'
        iFU = CWD / 'iteration-F-U.xlsx'
        return {
                'targets': [angles, anglesTxt, ryHistory, iFU],
                'file_dep': [h5, script, wingObj],
                'actions': [['python', script, analysis]],
                'clean': True
                }

    if analysis == 'nLinear':
        script = CWD / 'post.py'
        anglesTxt = CWD / 'RY.txt'
        angles = CWD / 'RY.mat'
        ryHistory = CWD / 'ryHistory.txt'
        iFU = CWD / 'iteration-F-U.xlsx'
        return {
                'targets': [angles, anglesTxt, ryHistory, iFU],
                'file_dep': [h5, script],
                'actions': [['python', script, analysis]],
                'clean': True
                }

    if analysis == 'modal':
        script = CWD / 'processModes.py'
        mod = CWD / 'results.mod'
        xlsx = CWD / 'results.xlsx'
        return {
                'targets': [mod, xlsx,],
                'file_dep': [h5, script, wingObj],
                'actions': [['python', script, 'model-modal.bdf']],
                'clean': True
                }

def task_loads():

    angles = CWD / 'RY.mat'
    loadFiles = [CWD / f'load_{load}.mat' for load in ['Uy', 'Uz', 'Um']]
    matScript = CWD / 'loads.m'

    return {
            'targets': loadFiles,
            'file_dep': [angles, matScript],
            # Read RY.mat file -> 0
            'actions': [[octave, matScript, '0']],
            'clean': True
            }

def task_allClean():

    analyses = ['linear', 'modal', 'nLinear', 'modal-nLinear-restart']
    suffixes = ['.op2', '.h5', '.out', '.sts']
    addSuffixes = ['.aeso', '.asm', '.becho', '.f04', '.f06', '.pch', '.plt', '.asg', '.log', \
                   '.IFPDAT', '.DBALL', '.MASTER', '.mod', '.xlsx']
    nastranFiles = [f'model-{an}{suf}' for an, suf in product(analyses, suffixes + addSuffixes)]
    # model.T7562777 files 
    g = list(CWD.glob('*.T*'))
    modalResults = ['modalResults.xlsx', 'results.mod']
    loadFiles = ['load_Um.mat', 'load_Uy.mat', 'load_Uz.mat']
    angleFiles = ['RY.mat', 'RY.txt']
    histories = [f'ryHistory-{an}.csv' for an in analyses]
    others = ['wing.obj']

    def unlinkFiles(files):
        for file in files:
            f = CWD / file
            f.unlink(missing_ok=True)

    return {
            'actions': [(unlinkFiles, [nastranFiles + modalResults + loadFiles \
                    + g + angleFiles + histories + others])],
            }
            
