import bpy
import math
import sys
import os
import numpy as np
import bmesh
import configparser
import json
import collections
import mathutils
import math
import subprocess
import copy

def camPosToQuaternion(cx, cy, cz):
    camDist = math.sqrt(cx * cx + cy * cy + cz * cz)
    cx = cx / camDist
    cy = cy / camDist
    cz = cz / camDist
    axis = (-cz, 0, cx)
    angle = math.acos(cy)
    a = math.sqrt(2) / 2
    b = math.sqrt(2) / 2
    w1 = axis[0]
    w2 = axis[1]
    w3 = axis[2]
    c = math.cos(angle / 2)
    d = math.sin(angle / 2)
    q1 = a * c - b * d * w1
    q2 = b * c + a * d * w1
    q3 = a * d * w2 + b * d * w3
    q4 = -b * d * w2 + a * d * w3
    return (q1, q2, q3, q4)

def quaternionFromYawPitchRoll(yaw, pitch, roll):
    c1 = math.cos(yaw / 2.0)
    c2 = math.cos(pitch / 2.0)
    c3 = math.cos(roll / 2.0)
    s1 = math.sin(yaw / 2.0)
    s2 = math.sin(pitch / 2.0)
    s3 = math.sin(roll / 2.0)
    q1 = c1 * c2 * c3 + s1 * s2 * s3
    q2 = c1 * c2 * s3 - s1 * s2 * c3
    q3 = c1 * s2 * c3 + s1 * c2 * s3
    q4 = s1 * c2 * c3 - c1 * s2 * s3
    return (q1, q2, q3, q4)


def camPosToQuaternion(cx, cy, cz):
    q1a = 0
    q1b = 0
    q1c = math.sqrt(2) / 2
    q1d = math.sqrt(2) / 2
    camDist = math.sqrt(cx * cx + cy * cy + cz * cz)
    cx = cx / camDist
    cy = cy / camDist
    cz = cz / camDist
    t = math.sqrt(cx * cx + cy * cy)
    tx = cx / t
    ty = cy / t
    yaw = math.acos(ty)
    if tx > 0:
        yaw = 2 * math.pi - yaw
    pitch = 0
    roll = math.acos(tx * cx + ty * cy)
    if cz < 0:
        roll = -roll
    q2a, q2b, q2c, q2d = quaternionFromYawPitchRoll(yaw, pitch, roll)
    q1 = q1a * q2a - q1b * q2b - q1c * q2c - q1d * q2d
    q2 = q1b * q2a + q1a * q2b + q1d * q2c - q1c * q2d
    q3 = q1c * q2a - q1d * q2b + q1a * q2c + q1b * q2d
    q4 = q1d * q2a + q1c * q2b - q1b * q2c + q1a * q2d
    return (q1, q2, q3, q4)

def obj_centened_camera_pos(dist, phi_deg, theta_deg):
    phi = float(phi_deg) / 180 * math.pi
    theta = float(theta_deg) / 180 * math.pi
    x = (dist * math.cos(theta) * math.cos(phi))
    y = (dist * math.sin(theta) * math.cos(phi))
    z = (dist * math.sin(phi))
    return (x, y, z)


def norm_2(v):
    return(math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]))


def get_rotation(r):
    x = -1*r
    z =  np.array([r[1],-r[0],0])
    y =  np.array([-1*r[0]*r[2],-1*r[2]*r[1],r[0]*r[0]+r[1]*r[1]])
    x = x/norm_2(x)
    y = y/norm_2(y)
    z = z/norm_2(z)
    M =  [x,y,z]
    R = [M[2],M[1],M[0]*-1]
    return (R)



coord_convert = mathutils.Matrix(((1,0,0),(0,0,-1),(0,1,0)))
convert_euler = coord_convert.to_euler('XYZ')

# MAIN script

bpy.data.scenes["Scene"].render.engine="CYCLES"
bpy.data.scenes['Scene'].render.resolution_x = 1600
bpy.data.scenes['Scene'].render.resolution_y = 1200
motion = dict()
cfgPath = sys.argv[5]
skip_factor = int(sys.argv[6])
#cfgPath = '~/projects/sound/sound/result/scene-0/obj-0-0-1/mat-0-0-0/sim/blender_render.cfg'
config=configparser.ConfigParser()
config.read(cfgPath)
outPath = config.get('OutPath','outpath')
#outPath = '/data/vision/billf/object-properties/sound/ztzhang/test'
motionPath = config.get('MotionFile','path')
with open(motionPath,'r') as motionfile:
    lines = motionfile.readlines()
for line in lines:
    content = line.strip('\n').split()
    # convert openGL coord to blender coord. Blender is standard interpretation.
    if float(content[1]) in motion.keys():

        motion[float(content[1])][int(content[0])]=dict()
        motion[float(content[1])][int(content[0])]['center'] = (float(content[2]),-float(content[4]),float(content[3])) 
        motion[float(content[1])][int(content[0])]['rotation']=((float(content[5]),float(content[6]),float(content[7])),
                                                                (-float(content[11]),-float(content[12]),-float(content[13])),
                                                                (float(content[8]),float(content[9]),float(content[10])))
        #print(motion[float(content[1])][int(content[0])]['rotation'])
    else:

        motion[float(content[1])]=dict()
        motion[float(content[1])][int(content[0])]=dict()
        motion[float(content[1])][int(content[0])]['center'] = (float(content[2]),-float(content[4]),float(content[3])) 
        motion[float(content[1])][int(content[0])]['rotation']=((float(content[5]),float(content[6]),float(content[7])),
                                                                (-float(content[11]),-float(content[12]),-float(content[13])),
                                                                (float(content[8]),float(content[9]),float(content[10])))
        #print(motion[float(content[1])][int(content[0])]['rotation'])
        
        
ordered_motion = collections.OrderedDict(sorted(motion.items()))

print('Motion Read!\n')

# Set up lightings
lightingPath = config.get('Lighting','path')
lightConfig = configparser.ConfigParser()
lightConfig.read(lightingPath)
numLight = lightConfig.getint('Lights','light_num')
style = lightConfig.get('Lights','style')
if style=='default':
    lightDist = 10
    # set lights
    for i in range(numLight):
        light_phi_deg = 45.0
        light_theta_deg = i * 360.0 / numLight
        lx, ly, lz = obj_centened_camera_pos(lightDist, light_phi_deg, light_theta_deg)
        bpy.ops.object.lamp_add(type='POINT', view_align = False, location=(lx, ly, lz))
        bpy.data.objects['Point'].data.energy = 2
else:
    for i in range(numLight):
        lightDist = lightConfig.getfloat('Light_%d'%i,'r')
        pointAt = json.loads(lightConfig.get('Light_%d'%i,'point_at'))
        theta = lightConfig.getfloat('Light_%d'%i,'theta')
        phi = lightConfig.getfloat('Light_%d'%i,'phi')
        energy = lightConfig.getfloat('Light_%d'%i,'energy')
        lightType = lightConfig.get('Light_%d'%i,'type')
        # Add light to scene
        scene = bpy.context.scene
        lamp_data = bpy.data.lamps.new(name='Lamp%d'%i, type=lightType)
        lamp_data.use_nodes = True
        lamp_object = bpy.data.objects.new(name='Lamp%d'%i, object_data=lamp_data)
        scene.objects.link(lamp_object)
        lx, ly, lz = obj_centened_camera_pos(lightDist, phi, theta)
        lamp_object.location = (lx+pointAt[0], ly+pointAt[1],lz+pointAt[2])
        lamp_data.node_tree.nodes['Emission'].inputs[1].default_value =energy*100
        lamp_data.cycles.cast_shadow = True
        
        if lightType!='POINT':
        #rotation for lights 
            r = np.array([-lx,-ly,lz])
            R =  get_rotation(r)
            rot = mathutils.Matrix(R)
            rot.transpose()
            rot_euler = rot.to_euler()
            lamp_object.rotation_euler = rot_euler

            
#Setup camera
bpy.ops.object.camera_add()
camObj = bpy.data.objects['Camera']
camPath = config.get('Camera','path')
camConfig = configparser.ConfigParser()
camConfig.read(camPath)
lookAt = json.loads(camConfig.get('Camera','look_at'))
rho = camConfig.getfloat('Camera','r')
phi = camConfig.getfloat('Camera','phi')
theta = camConfig.getfloat('Camera','theta')
focal_length = camConfig.getfloat('Camera','focal_length')
sensor_width = camConfig.getfloat('Camera','sensor_width')
# set position

cx, cy, cz = obj_centened_camera_pos(rho, phi, theta)

#print cx,cy,cz
r = np.array([-cx,-cy,cz])
R =  get_rotation(r)
rot = mathutils.Matrix(R)
rot.transpose()
rot_euler = rot.to_euler()

camObj.location[0] = cx+lookAt[0]
camObj.location[1] = cy+lookAt[1]
camObj.location[2] = cz+lookAt[2]
camObj.rotation_mode = 'XYZ'
camObj.rotation_euler=rot_euler

#print(camObj.rotation_euler)



bpy.data.scenes[0].camera=camObj
# set properties
bpy.data.cameras[0].lens = focal_length
bpy.data.cameras[0].sensor_width = sensor_width


# Import objects
# Assume each mesh is centered at zero
objnum = config.getint('Objects','obj_num')
for objid in range(0,objnum):
    obj_path = config.get('Objects','obj_%d'%objid)
    bpy.ops.import_scene.obj(filepath = obj_path,axis_forward='X', axis_up='Y')
    bpy.context.selected_objects[0].name = 'mesh%d'%objid
    
    obj_rotation = json.loads(config.get('Objects','obj_%d_rot'%objid))
    
    #print(objid)
    quat = mathutils.Quaternion([obj_rotation[3],obj_rotation[0],obj_rotation[1],obj_rotation[2]])
    m1 = quat.to_matrix()
    #print(m1)

    
    
    M = mathutils.Matrix(((1,0,0),(0,0,-1),(0,1,0)))
    ########
    m2 = m1

    
    obj_euler = m2.to_euler('XYZ')
    
    current_obj = bpy.data.objects['mesh%d'%objid]
    #print(current_obj.rotation_euler)
    current_obj.rotation_mode='XYZ'
    current_obj.rotation_euler = obj_euler
    #print(current_obj.rotation_euler)
    #bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    #print(current_obj.rotation_euler)
    #bpy.data.objects['mesh%d'%objid].rotation_euler = convert_euler
    #bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    '''
    for x in range(len(current_obj.material_slots)):
        mat = current_obj.material_slots[x]
        if mat.name[0:7]=='texture':
            #print(mat.name)
            filename =""
            ext = ""
            cnt = 0
            for x in range(8,len(mat.name)):
                if cnt == 0 and mat.name[x]!='-':
                    filename+=mat.name[x]
                elif cnt == 0 and mat.name[x]=='-':
                    cnt = 1
                elif cnt == 1:
                    ext+=mat.name[x]
            matdata = bpy.data.materials[mat.name]
            matdata.name = '%d-%s'%(objid,mat.name)
            matdata.use_nodes = True
            nt = matdata.node_tree
            nodes = nt.nodes
            links = nt.links
            diffuse = nodes['Diffuse BSDF']
            texture = nodes.new('ShaderNodeTexImage')
            dirs = obj_path.split('/')
            imgpath = os.path.join('/',*(dirs[0:-1]),'images','%s.%s'%(filename,ext))
            texture.image = bpy.data.images.load(imgpath)
            links.new(diffuse.inputs['Color'],texture.outputs['Color'])
            #print(filename+'.'+ext)
            #print(mat.name)
    '''



print('Imported! Read!\n')

#assume a 300 fps simulation
#render 30 at fps



#bpy.context.user_preferences.system.compute_device_type = 'CUDA'
#bpy.context.user_preferences.system.compute_device = 'CUDA_MULTI_2'
#bpy.data.scenes['Scene'].cycles.device = 'GPU'

fps = 300
samples = range(0,len(ordered_motion.keys()),int(fps/30)*skip_factor)
ke = list(ordered_motion.keys())

XYZ_cache = dict()
euler_cache = dict()
time_stamp_cache = 0


for s in samples:
    time_stamp = ke[s]
    print(time_stamp)
    if time_stamp>=0.001:
        flag = 0
        for objid in ordered_motion[time_stamp].keys():
            current_obj = bpy.data.objects['mesh%d'%objid]
            current_obj.location = ordered_motion[time_stamp][objid]['center']
            euler = mathutils.Matrix(ordered_motion[time_stamp][objid]['rotation']).to_euler('XYZ')
            #print('-----%d------'%objid)
            #print(euler)
            current_obj.rotation_mode='XYZ'
            current_obj.rotation_euler = euler

            ## Check if hits cache
            if current_obj.location[0]!=XYZ_cache[objid][0] or current_obj.location[1]!=XYZ_cache[objid][1]\
            or current_obj.location[2]!=XYZ_cache[objid][2] :
                flag=1
                print(current_obj.location)
                print(XYZ_cache[objid])
            if current_obj.rotation_euler[0]!=euler_cache[objid][0] or current_obj.rotation_euler[1]!=euler_cache[objid][1]\
            or current_obj.rotation_euler[2]!=euler_cache[objid][2]:
                flag=1
                print(current_obj.rotation_euler)
                print(euler_cache[objid])

            ##update cache 
            XYZ_cache[objid] = copy.deepcopy(current_obj.location)
            euler_cache[objid] = mathutils.Matrix(ordered_motion[time_stamp][objid]['rotation']).to_euler('XYZ')

        # cache misses, render scene
        if flag==1:
            print("MISS!!!!")
            bpy.data.scenes['Scene'].render.filepath = outPath+'/%.5f.png'%time_stamp
            bpy.ops.render.render( write_still = True )
            time_stamp_cache = time_stamp
        #cache hits, copy prev:
        else:
            print("HIT!!!!")
            prev = outPath+'/%.5f.png'%time_stamp_cache
            current = outPath+'/%.5f.png'%time_stamp
            subprocess.call('cp %s %s'%(prev,current),shell=True)
            time_stamp_cache = time_stamp


    else:
        for objid in ordered_motion[time_stamp].keys():

            current_obj = bpy.data.objects['mesh%d'%objid]
            current_obj.location = ordered_motion[time_stamp][objid]['center']
            euler = mathutils.Matrix(ordered_motion[time_stamp][objid]['rotation']).to_euler('XYZ')

            current_obj.rotation_mode='XYZ'
            current_obj.rotation_euler = euler

            ## INIT CACHE
            XYZ_cache[objid] = copy.deepcopy(current_obj.location)
            euler_cache[objid] = mathutils.Matrix(ordered_motion[time_stamp][objid]['rotation']).to_euler('XYZ')
            time_stamp_cache = time_stamp

        bpy.data.scenes['Scene'].render.filepath = outPath+'/%.5f.png'%time_stamp
        bpy.ops.render.render( write_still = True )        






    
