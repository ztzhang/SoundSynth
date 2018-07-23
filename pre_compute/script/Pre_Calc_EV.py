import sys
import configparser as ConfigParser
import os
import subprocess


ROOT_DIR = '..'
DATASET_NAME = 'final100'

MODALSOUND = ROOT_DIR + '/modal_sound/build/bin'
EXTMAT = MODALSOUND + '/extmat'
GENMOMENTS = MODALSOUND + '/gen_moments'
FILEGENERATORS = ROOT_DIR + '/file_generator'


class Obj:
    ROOT = ROOT_DIR

    def __init__(self, objId=0, matId=0):
        self.objId = objId
        self.matId = matId
        self.Load()

    def ReadMaterial(self, matId):
        self.matId = matId
        matCfg = ConfigParser.ConfigParser()
        cfgPath = os.path.join(self.ROOT, 'config',
                               'material', 'material-%d.cfg' % self.matId)
        matCfg.read(cfgPath)

        self.materialName = matCfg.get('DEFAULT', 'name')
        self.youngsModulus = matCfg.getfloat('DEFAULT', 'youngs')
        self.poissonRatio = matCfg.getfloat('DEFAULT', 'poison')
        self.density = matCfg.getfloat('DEFAULT', 'density')
        self.alpha = matCfg.getfloat('DEFAULT', 'alpha')
        self.beta = matCfg.getfloat('DEFAULT', 'beta')
        self.friction = matCfg.getfloat('DEFAULT', 'friction')
        self.restitution = matCfg.getfloat('DEFAULT', 'restitution')
        self.rollingFriction = matCfg.getfloat('DEFAULT', 'rollingFriction')
        self.spinningFriction = matCfg.getfloat('DEFAULT', 'spinningFriction')

    def ReadObj(self, objId):
        self.objId = objId
        self.objPath = os.path.join(
            self.ROOT, 'data', DATASET_NAME, '%d' % self.objId, 'models', '%d.orig.obj' % self.objId)

    def ReadTet(self):
        self.tetPath = os.path.join(
            self.ROOT, 'data', DATASET_NAME, '%d' % self.objId, 'models', 'obj-%d.tet' % self.objId)

    def Load(self):
        self.ReadMaterial(self.matId)
        self.ReadObj(self.objId)
        self.ReadTet()


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def CreateDir(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    argv = sys.argv
    obj_id = int(argv[1])
    mat_id = int(argv[2])
    overwrite = int(argv[3])
    print(overwrite)
    obj = Obj(obj_id, mat_id)
    objfilePath = os.path.join(
        ROOT_DIR, 'data', DATASET_NAME, '%d' % obj.objId, 'models')
    outPath = os.path.join(ROOT_DIR, 'data', DATASET_NAME, '%d' %
                           obj.objId, 'models', 'mat-%d' % obj.matId)
    CreateDir(outPath)
    # call extmat, save to root
    with cd(outPath):
        logfile = 'precalc.log'
        if not os.path.exists('obj-%d.tet' % obj.objId) or overwrite == 1:

            subprocess.call('ln -s ../obj-%d.tet obj-%d.tet' %
                            (obj.objId, obj.objId), shell=True)

        if not os.path.exists('obj-%d.stiff.spm' % obj.objId) or not os.path.exists('obj-%d.mass.spm' % obj.objId) or overwrite == 1:
            cmd = EXTMAT + ' -f obj-%d -y %.4g -p %.5g -m -k -g -s -d 1 | tee -a %s' % (
                obj.objId, obj.youngsModulus, obj.poissonRatio, logfile)
            subprocess.call(cmd, shell=True)

    # call ev calculation, save to mat-id
        print('EV!')
        if not os.path.exists('obj-%d.ev' % obj.objId) or overwrite == 1:

            cmd = 'matlab -nodisplay -nodesktop -nosplash -r "addpath(\'%s\'); ev_generator60(\'%s\', 60); quit"| tee -a %s' % (
                FILEGENERATORS, 'obj-%d' % obj.objId, logfile)
            subprocess.call(cmd, shell=True)

    # Geo maps
        if not os.path.exists('obj-%d.vmap' % obj.objId) or overwrite == 1:
            cmd = '%s/vmap_generator obj-%d.geo.txt obj-%d.vmap | tee -a %s' % (
                FILEGENERATORS, obj.objId, obj.objId, logfile)
            subprocess.call(cmd, shell=True)
        CreateDir(os.path.join(outPath, 'bem_input'))
        CreateDir(os.path.join(outPath, 'bem_result'))
        CreateDir(os.path.join(outPath, 'fastbem'))
        if not os.path.exists('./bem_input/init_bem.mat') or \
                not os.path.exists('./bem_input/mesh.mat') or\
                not os.path.exists('./bem_input/init_bem.mat') or overwrite == 1:
            cmd = 'matlab -nodisplay -nodesktop -nosplash -r "addpath(\'%s\');BEMInputGenerator(\'%s\', \'obj-%d\', %.5g, %.5g, %.5g,%d); quit" | tee -a %s'\
                % (FILEGENERATORS, outPath, obj.objId, obj.density, obj.alpha, obj.beta, overwrite, logfile)
            subprocess.call(cmd, shell=True)
