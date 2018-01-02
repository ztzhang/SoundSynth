# this is a script for Generating video with sound, using precomputed
# pressure field.
import sys
import getopt
import configparser as ConfigParser
import os
import json
import subprocess
import math
import getopt


ROOT_DIR = os.path.abspath(os.path.dirname(sys.argv[0])) + '/../'
ROOT_DIR = os.path.abspath(ROOT_DIR)
BLENDER = '/data/vision/billf/object-properties/sound/software/blender/blender'


class Obj:
    ROOT = ROOT_DIR

    def __init__(self, objId=0, matId=0):
        self.objId = objId
        self.center = [0, 0, 0]
        self.rotation = [0, 0, 0, 1]
        self.matId = matId
        self.poseId = 0
        self.bulletSetupId = 0
        self.mass = 1
        self.active = 1

    def ReadPose(self, poseId):
        self.poseId = poseId
        poseCfg = ConfigParser.ConfigParser()
        cfgPath = os.path.join(self.ROOT, 'config', 'pose',
                               'pose_%d.cfg' % self.poseId)
        poseCfg.read(cfgPath)
        self.center = json.loads(poseCfg.get('DEFAULT', 'center'))
        self.rotation = json.loads(poseCfg.get('DEFAULT', 'rotation'))
        self.linearVelocity = json.loads(
            poseCfg.get('DEFAULT', 'linear_velocity'))
        self.angularVelocity = json.loads(
            poseCfg.get('DEFAULT', 'angular_velocity'))

    def ReadBulletSetup(self, bulletSetupId):
        self.bulletSetupId = bulletSetupId
        bulletCfg = ConfigParser.ConfigParser()
        cfgPath = os.path.join(
            self.ROOT, 'config', 'bullet_setup', 'bullet_%d.cfg' % self.bulletSetupId)
        bulletCfg.read(cfgPath)
        self.linearDamping = bulletCfg.getfloat('DEFAULT', 'linearDamping')
        self.angularDamping = bulletCfg.getfloat('DEFAULT', 'angularDamping')
        self.collisionMargin = bulletCfg.getfloat('DEFAULT', 'collisionMargin')

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
        if self.active == 1:
            self.objPath = os.path.join(
                self.ROOT, 'data/ready', '%d' % self.objId, '%d.orig_nt.obj' % self.objId)
        else:
            self.objPath = os.path.join(
                self.ROOT, 'data/ready', '%d' % self.objId, '%d.orig.obj' % self.objId)
        if self.active == 1:
            volumefile = open(os.path.join(
                self.ROOT, 'data/final100/%d/models/volume.txt' % self.objId))
            self.mass = float(volumefile.readline()) * self.density / 50

    def Load(self):
        self.ReadPose(self.poseId)
        self.ReadBulletSetup(self.bulletSetupId)
        self.ReadMaterial(self.matId)
        self.ReadObj(self.objId)

    def PrintStat(self):
        print('obj #%d:\n' % self.objId)
        print('        material: #%d\n' % self.matId)
        print('        initial pose: #%d\n' % self.poseId)
        print('        bullet simulation setup: #%d\n' % self.bulletSetupId)

    def WriteString(self):
        properties = ''
        properties += '%.4f %.4f ' % (self.mass, self.collisionMargin)
        properties += '%.2f %.2f %.2f %.2f ' % tuple(self.rotation)
        properties += '%.2f %.2f %.2f 0 ' % tuple(self.center)
        properties += '%.2f %.2f %.2f ' % tuple(self.linearVelocity)
        properties += '%.2f %.2f %.2f ' % tuple(self.angularVelocity)
        properties += '%.2f %.2f %.2f ' % (self.friction,
                                           self.restitution, self.rollingFriction)
        properties += '%.2f %.2f %.2f\n' % (self.spinningFriction,
                                            self.linearDamping, self.angularDamping)
        return properties

    def WriteShellCmd(self):
        cmd = '-n %d -d %f -A %1.5e -B %f' % (self.objId,
                                              self.density, self.alpha, self.beta)
        return cmd


class Cam:
    ROOT = ROOT_DIR

    def __init__(self, cfgId=0):
        self.cfgId = cfgId
        self.cfgPath = os.path.join(
            self.ROOT, 'config', 'camera', 'camera_%d.cfg' % cfgId)
        self.Load()

    def SetCfgId(self, cfgId):
        self.cfgId = cfgId
        self.cfgPath = os.path.join(
            self.ROOT, 'config', 'camera', 'camera_%d.cfg' % cfgId)
        self.Load()

    def Load(self):
        camCfg = ConfigParser.ConfigParser()
        camCfg.read(self.cfgPath)
        self.lookAt = json.loads(camCfg.get('Camera', 'look_at'))
        self.r = camCfg.getfloat('Camera', 'r')
        self.theta = camCfg.getfloat('Camera', 'theta')
        self.phi = camCfg.getfloat('Camera', 'phi')
        self.focalLength = camCfg.getint('Camera', 'focal_length')
        self.sensorWidth = camCfg.getint('Camera', 'sensor_width')
        self.CalcXYZ()

    def CalcXYZ(self):
        x = self.r * math.sin(math.radians(self.theta)) * \
            math.cos(math.radians(self.phi))
        y = self.r * math.sin(math.radians(self.theta)) * \
            math.sin(math.radians(self.phi))
        z = self.r * math.cos(math.radians(self.theta))
        self.xyz = [x, y, z]


class Lighting:
    ROOT = ROOT_DIR

    def __init__(self, cfgId=0):
        self.cfgId = cfgId
        self.cfgPath = os.path.join(
            self.ROOT, 'config', 'lighting', 'lighting_%d.cfg' % cfgId)

    def SetCfgId(self, cfgId):
        self.cfgId = cfgId
        self.cfgPath = os.path.join(
            self.ROOT, 'config', 'lighting', 'lighting_%d.cfg' % cfgId)

    def PrintPath(self):
        return self.cfgPath


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

# This script would read in a scene configuration, which includes:
#        1.Object number
#        2.Their initial velocity position and pose
#        3.Camera position
#        4.Simulation Parameters, i.e. FPS, collision margin, duration, etc.
#        5.Lights
#
#        Need to specify a scene id and corresponding obj id with materials id.


if __name__ == '__main__':
    ROOT = ROOT_DIR

    args = sys.argv[1:]
    optlist, args = getopt.getopt(args, 'bsrcop:v')
    argv = [sys.argv[0]] + args
    skip_bullet = False
    skip_sound = False
    skip_rendering = False
    is_overwrite = True
    skip_factor = 1
    skip_video = False
    for k, v in optlist:
        if k == '-b':
            skip_bullet = True
        elif k == '-s':
            skip_sound = True
        elif k == '-r':
            skip_rendering = True
        elif k == '-c':
            is_overwrite = False
        elif k == '-p':
            skip_factor = int(v)
        elif k == '-v':
            skip_video = True

    # print sys.argv

    # READ SCENE CONFIG
    if (len(argv) < 2):
        print('Not enough argument, Scene ID needed! \n')

    sceneid = int(argv[1])
    sceneConfig = ConfigParser.ConfigParser()
    sceneConfig.read(os.path.join(
        ROOT_DIR, 'config/scene/scene_%d.cfg' % sceneid))

    # Get Objs
    objnum = sceneConfig.getint('Objects', 'obj_num')
    if(len(argv) < (2 + 2 * objnum)):
        print('not enough arguemnt! using default objects and materials\n')
        objs = [Obj(0, 0) for x in range(objnum)]
    else:
        objs = []
        for k in range(objnum):
            objs.append(
                Obj(objId=int(argv[k * 2 + 2]), matId=int(argv[k * 2 + 3])))

    for objid in range(objnum):
        objs[objid].poseId = (sceneConfig.getint(
            'Objects', 'obj_%d_pose' % objid))
        objs[objid].bulletSetupId = (sceneConfig.getint(
            'Objects', 'obj_%d_bullet_setup' % objid))
        if sceneConfig.getint('Objects', 'obj_%d_is_active' % objid) == 0:
            objs[objid].active = 0
            objs[objid].mass = 0
        objs[objid].Load()

    # Log set up:
    print('Total %d objects:\n' % objnum)

    for objid in range(objnum):
        objs[objid].PrintStat()

    # READ CAMERA CONFIG
    cam = Cam(sceneConfig.getint('Camera', 'Camera'))
    print('Using camera setup #%d\n' % cam.cfgId)

    # READ LIGHTING CONFIG
    lighting = Lighting(sceneConfig.getint('Lighting', 'lighting'))
    print('Using lighting setup #%d\n' % lighting.cfgId)

    # READ BULLET Simulation Setup
    simId = 0
    simCfg = ConfigParser.ConfigParser()
    simCfg.read(os.path.join(ROOT, 'config',
                             'simulation', 'sim_%d.dat' % simId))
    FPS = simCfg.getint('DEFAULT', 'FPS')
    ifGUI = simCfg.getint('DEFAULT', 'GUI')
    duration = simCfg.getfloat('DEFAULT', 'duration')

    # CREATE RESULT PATH
    objResultPath = 'obj'
    matResultPath = 'mat'

    for k in range(objnum):
        objResultPath += '-%d' % objs[k].objId
        matResultPath += '-%d' % objs[k].matId

    resultPath = os.path.join(ROOT, 'result_v1_1', 'scene-%d' %
                              sceneid, objResultPath, matResultPath)
    simFilePath = os.path.join(resultPath, 'sim')
    renderPath = os.path.join(resultPath, 'render')
    CreateDir(resultPath)
    CreateDir(renderPath)
    CreateDir(simFilePath)

    # Physical simulation
    # Need to prepare dat files for bullet simulation
    bulletCfg = open(os.path.join(simFilePath, 'bullet.cfg'), 'w')
    bulletCfg.write('%d\n%d\n%.2f\n' % (ifGUI, FPS, duration))
    bulletCfg.write('%.5f\n%.5f\n%.5f\n' % (cam.r, cam.theta, cam.phi))
    bulletCfg.write('%.5f\n%.5f\n%.5f\n' % tuple(cam.lookAt))
    bulletCfg.close()
    bltInputCfg = open(os.path.join(simFilePath, 'bullet.input.dat'), 'w')
    bltInputCfg.write('%d\n' % (objnum))

    for obj_id in range(0, objnum):
        bltInputCfg.write('%d %d ' % (
            obj_id, objs[obj_id].objId) + objs[obj_id].WriteString())

    bltInputCfg.close()
    with cd(simFilePath):
        if skip_bullet is not True:
            for obj in objs:
                print(
                    "-------------------bullet--------%d-----------------------------" % obj.objId)
                if not os.path.exists('%d.obj' % obj.objId):
                    subprocess.call('ln -s %s' % os.path.join(ROOT, 'data/ready', '%d' % obj.objId, '%d.obj' % obj.objId)
                                    + ' %d.obj' % obj.objId, shell=True)
                if not os.path.exists('%d.orig.obj' % obj.objId):
                    subprocess.call('ln -s %s' % os.path.join(ROOT, 'data/ready', '%d' % obj.objId, '%d.orig.obj' % obj.objId)
                                    + ' %d.orig.obj' % obj.objId, shell=True)
                # print 'ln -s %s'%os.path.join(ROOT,'data/ready','%d'%obj.objId,'%d.obj'%obj.objId)
                # print 'ln -s
                # %s'%os.path.join(ROOT,'data/ready','%d'%obj.objId,'%d.orig.obj'%obj.objId)
            subprocess.call('sh %s >log1.txt' % os.path.join(
                ROOT, 'online_synth', 'prepare_dat.sh'), shell=True)

        if skip_sound is not True:
            for obj_id in range(0, objnum):
                if(objs[obj_id].mass == 0):
                    continue
                # print objs[obj_id].WriteShellCmd()
                print("---------------------------%d-----------------------------" %
                      objs[obj_id].objId)
                if os.path.exists('%d.vmap' % objs[obj_id].objId):
                    subprocess.call('unlink %d.vmap' %
                                    objs[obj_id].objId, shell=True)
                subprocess.call('ln -s %s' % os.path.join(ROOT, 'data/ready', '%d' % objs[obj_id].objId,
                                                          'mat-%d' % objs[obj_id].matId, 'obj-%d.vmap' % objs[obj_id].objId)
                                + ' %d.vmap' % objs[obj_id].objId, shell=True)

                if os.path.exists('moments'):
                    subprocess.call('unlink moments', shell=True)
                subprocess.call('ln -s %s' % os.path.join(ROOT, 'data/ready', '%d' % objs[obj_id].objId,
                                                          'mat-%d' % objs[obj_id].matId, 'moments') + ' moments', shell=True)

                if os.path.exists('%d.geo.txt' % objs[obj_id].objId):
                    subprocess.call('unlink %d.geo.txt' %
                                    objs[obj_id].objId, shell=True)
                subprocess.call('ln -s %s' % os.path.join(ROOT, 'data/ready', '%d' % objs[obj_id].objId,
                                                          'mat-%d' % objs[obj_id].matId, 'obj-%d.geo.txt' % objs[obj_id].objId) +
                                ' %d.geo.txt' % objs[obj_id].objId, shell=True)

                if os.path.exists('%d.ev' % objs[obj_id].objId):
                    subprocess.call('unlink %d.ev' %
                                    objs[obj_id].objId, shell=True)
                subprocess.call('ln -s %s' % os.path.join(ROOT, 'data/ready', '%d' % objs[obj_id].objId,
                                                          'mat-%d' % objs[obj_id].matId, 'obj-%d.ev' % objs[obj_id].objId) +
                                ' %d.ev' % objs[obj_id].objId, shell=True)

                print('sh %s' % os.path.join(ROOT, 'script', 'prepare_ini.sh') + ' -i %d ' % obj_id
                      + objs[obj_id].WriteShellCmd())

                if os.path.exists('../%04d.wav' % (objs[obj_id].objId)):
                    print('WAV FOUND!')
                if os.path.exists('../%04d.raw' % (objs[obj_id].objId)):
                    print('RAW FOUND!')

                if is_overwrite:
                    print("OVERWRITE!!!")
                    subprocess.call('rm *.wav', shell=True)
                    subprocess.call('rm *.raw', shell=True)
                    if os.path.exists('../%04d.wav' % (objs[obj_id].objId)):
                        subprocess.call('rm ../%04d.wav' %
                                        (objs[obj_id].objId), shell=True)

                if not os.path.exists('./../%04d.wav' % (obj_id)) or not os.path.exists('./../%04d.raw' % (obj_id)):
                    print('wav not generated yet, working on it !')
                    subprocess.call('rm *.wav', shell=True)
                    subprocess.call('rm *.raw', shell=True)
                    subprocess.call('bash %s' % os.path.join(ROOT, 'online_synth', 'prepare_ini.sh') + ' -i %d ' % obj_id
                                    + objs[obj_id].WriteShellCmd(), shell=True)
                    if not os.path.exists('continuous_audio1.wav'):
                        subprocess.call('echo %d sound failed! > %d.txt' % (
                            objs[obj_id].objId, objs[obj_id].objId), shell=True)
                    subprocess.call('mv *1.wav ./../%04d.wav' %
                                    (obj_id), shell=True)
                    subprocess.call('mv *1.raw ./../%04d.raw' %
                                    (obj_id), shell=True)

                subprocess.call('unlink %d.vmap' %
                                objs[obj_id].objId, shell=True)
                subprocess.call('mv moments moments-%d' %
                                (objs[obj_id].objId), shell=True)
                subprocess.call('unlink %d.geo.txt' %
                                objs[obj_id].objId, shell=True)
                subprocess.call('unlink %d.ev' %
                                objs[obj_id].objId, shell=True)
                #subprocess.call('unlink %d.obj'%obj.objId,shell=True)
                #subprocess.call('unlink %d.orig.obj'%obj.objId,shell=True)
            # copy all wav file to parent folder
            #subprocess.call('mv *.wav ./../',shell=True)

        if skip_rendering != True and (not os.path.exists('./../sli.mp4') or is_overwrite):
            # subprocess.call(
            #    'sh /data/vision/billf/object-properties/sound/sound/script/unset.sh', shell=True)
            # Create cfg for rendering
            blendercfg = ConfigParser.ConfigParser()
            blendercfg.add_section('Objects')
            blendercfg.set('Objects', 'obj_num', '%d' % objnum)
            for obj_id in range(objnum):
                blendercfg.set('Objects', 'obj_%d' %
                               obj_id, '%s' % objs[obj_id].objPath)
                blendercfg.set('Objects', 'obj_%d_rot' % obj_id,
                               '[%f,%f,%f,%f]' % tuple(objs[obj_id].rotation))

            blendercfg.add_section('OutPath')
            blendercfg.set('OutPath', 'outpath', '%s' % renderPath)
            blendercfg.add_section('Camera')
            blendercfg.set('Camera', 'path', '%s' % cam.cfgPath)
            blendercfg.add_section('Lighting')
            blendercfg.set('Lighting', 'path', '%s' % lighting.cfgPath)
            blendercfg.add_section('MotionFile')
            blendercfg.set('MotionFile', 'path', '%s' %
                           os.path.join(simFilePath, 'motion.dat'))

            with open('blender_render.cfg', 'w+') as configfile:
                blendercfg.write(configfile)

            # unset python path, call blender and source
            blank = os.path.join(ROOT, 'script', 'blank.blend')
            blenderScript = os.path.join(
                ROOT, 'script', 'blender_render_scene.py')
            subprocess.call('unset PYTHONPATH', shell=True)
            subprocess.call('%s %s --background --python %s %s %d' % (BLENDER, blank, blenderScript,
                                                                      os.path.join(simFilePath, 'blender_render.cfg'), skip_factor), shell=True)
            #subprocess.call('source ~/.bash_profile',shell = True)
    if skip_video != True:
        actobj_num = []
        for obj in objs:
            if obj.mass != 0:
                actobj_num.append(obj)
        ffmpeg_video_cmd =\
            'ffmpeg -r 30 -pattern_type glob -i \'./render/*.png\' -pix_fmt yuv420p -crf 0 -vcodec libx264 sli.mp4 -y'
        ffmpeg_audio_cmd = 'ffmpeg '
        if len(actobj_num) == 1:
            ffmpeg_audio_cmd = 'cp obj-%04d.wav merged.wav' % (
                actobj_num[0].objId)
        else:
            for k in range(0, len(actobj_num)):
                ffmpeg_audio_cmd += '-i obj-%04d.wav ' % (actobj_num[k].objId)
            ffmpeg_audio_cmd += '-filter_complex -filter_complex amix=inputs=%d:duration=longest merged.wav -y' % (
                len(actobj_num))
        ffmpeg_movie_cmd = 'ffmpeg -i sli.mp4 -i merged.wav -crf 0 -vcodec libx264 result.mp4 -y'
        with cd(resultPath):
            #subprocess.call('rm -rf sli.mp4 merged.wav result.mp4',shell=True)
            print('calling %s\n' % ffmpeg_video_cmd)
            subprocess.call(ffmpeg_video_cmd, shell=True)
            print('calling %s\n' % ffmpeg_audio_cmd)
            subprocess.call(ffmpeg_audio_cmd, shell=True)
            print('calling %s\n' % ffmpeg_movie_cmd)
            subprocess.call(ffmpeg_movie_cmd, shell=True)
