
import sys
import numpy as np
import math

gravity = 10.0  # default for now


def get_Q(axis, angle):  # angle is -rele or -razi
    d = 1.0
    s = math.sin(angle * 0.5) / d
    mfloat = np.array([axis[0] * s, axis[1] * s, axis[2]
                       * s, math.cos(angle * 0.5)])
    return mfloat


def get_M(q):  # q is roll or rot
    d = 1.0  # len(q)^2
    s = 2.0 / d
    xs = q[0] * s
    ys = q[1] * s
    zs = q[2] * s
    wx = q[3] * xs
    wy = q[3] * ys
    wz = q[3] * zs
    xx = q[0] * xs
    xy = q[0] * ys
    xz = q[0] * zs
    yy = q[1] * ys
    yz = q[1] * zs
    zz = q[2] * zs
    M = np.array([[1.0 - yy - zz, xy - wz, xz + wy], [xy + wz,
                                                      1 - xx - zz, yz - wx], [xz - wy, yz + wx, 1 - xx - yy]])
    return M


def getDistance(pointCoord, vtx1, vtx2, vtx3):
    centroid = np.mean([vtx1, vtx2, vtx3], axis=0)
    distance = np.linalg.norm(pointCoord - centroid)
    return distance


def obj_centened_camera_pos(dist, phi_deg, theta_deg):
    phi = float(phi_deg) / 180 * math.pi
    theta = float(theta_deg) / 180 * math.pi
    x = (dist * math.cos(theta) * math.cos(phi))
    y = (dist * math.sin(theta) * math.cos(phi))
    z = (dist * math.sin(phi))
    xyz = np.array([x, y, z])
    return xyz


assert (len(sys.argv) ==
        3), "Usage: get_collision_info.py <bullet.input.dat> <collision_motion.dat>"
objFile = sys.argv[1]
cmFile = sys.argv[2]
# fileIn_2 = sys.argv[3]
# fileOut = sys.argv[4]
bulletcfg = open("bullet.cfg", "r").readlines()
fps = float(bulletcfg[1].strip())
print("FPS is %f" % fps)

ID2obj = {}  # map ID to obj file name
ID2index = {}  # map ID to index of collisionFiles and motionFiles
ID2mass = {}
obj = open(objFile, "r")
first_line = 1
for line in obj:
    if first_line == 1:
        first_line -= 1
    else:
        ID2obj[line.split()[0]] = line.split()[1] + ".obj"
        ID2mass[line.split()[0]] = float(line.split()[2])
obj.close()

first_line = 1

collisionFiles = []
motionFiles = []
campos_glob = np.array([0.0, 0.0, 0.0])
max_impulse = 0.0

cm = open(cmFile, "r")
current_index = 0
for line in cm.readlines():
    if first_line == 1:
        line = line.split()
        first_line -= 1
        distance = float(line[0])
        yaw = float(line[1])  # should be pitch?
        pitch = float(line[2])  # should be yaw?
        look_at_x = float(line[3])
        look_at_y = float(line[4])
        look_at_z = float(line[5])

        # rele = pitch *3.141592653589/180.0  # good
        # razi = yaw *3.141592653589/180.0    # good
        eyePos = obj_centened_camera_pos(distance, yaw, pitch)  # problem ?
        eye_target = np.array([look_at_x, look_at_y, look_at_z])
        #right = np.array([-1.0, 0.0, 0.0])
        #up = np.array([0.0, 1.0, 0.0])

        #rot = get_Q(up,razi)
        #roll = get_Q(right,-rele)

        #roll_3x3 = get_M(roll)
        #rot_3x3 = get_M(rot)
        #eyePos = np.dot(np.dot(rot_3x3, roll_3x3), eyePos)
        camPos = eyePos + eye_target

        campos_glob[0] = camPos[0]
        campos_glob[1] = camPos[2]
        campos_glob[2] = -camPos[1]

    else:
        currentLine = line.split()
        if len(currentLine) == 9:
            ID = currentLine[0]
            if not ID in ID2index:
                ID2index[ID] = current_index
                current_index += 1
                collisionFiles.append([])
                motionFiles.append([])
            index = ID2index[ID]
            collisionFiles[index].append(currentLine)
            if float(currentLine[8]) > max_impulse:
                max_impulse = float(currentLine[8])
        else:
            assert (len(currentLine) == 14), "Incorrect file format."
            ID = currentLine[0]
            index = ID2index[ID]
            motionFiles[index].append(currentLine)

print("Generating filtered version.")
for ID in ID2index:
    index = ID2index[ID]
    objFile = ID2obj[ID]
    mass = ID2mass[ID]
    collisionFile = collisionFiles[index]
    motionFile = motionFiles[index]
    fileOut = "collision_output-" + str(ID) + ".dat"

    time = []
    collisionPoint = np.array([0.0, 0.0, 0.0])
    impulseNormalX = []
    impulseNormalY = []
    impulseNormalZ = []
    impulseMag = []
    force = {}

    campos_obj = []

    for currentLine in collisionFile:
        assert (len(currentLine) == 9), "Incorrect file format."
        next_time = float(currentLine[1])
        next_normal = [float(currentLine[5]), float(
            currentLine[6]), float(currentLine[7])]
        next_impulse = float(currentLine[8])
        if next_time not in force:
            force[next_time] = next_impulse * \
                np.dot(np.asarray(next_normal), np.array([0, 1, 0]))
        else:
            force[next_time] += next_impulse * \
                np.dot(np.asarray(next_normal), np.array([0, 1, 0]))

    weight = mass * gravity * 1 / fps
    margin = weight * 7 / 100
    # read collision input file
    for currentLine in collisionFile:
        assert (len(currentLine) == 9), "Incorrect file format."
        next_time = float(currentLine[1])
        if abs(force[next_time] + weight) > margin:
            time.append(currentLine[1])
            collisionPoint = np.vstack((collisionPoint, np.array(
                [float(currentLine[2]), float(currentLine[3]), float(currentLine[4])])))
            impulseNormalX.append(float(currentLine[5]))
            impulseNormalY.append(float(currentLine[6]))
            impulseNormalZ.append(float(currentLine[7]))
            impulseMag.append(float(currentLine[8]))

    collisionPoint = np.delete(collisionPoint, 0, 0)

    # read motion file

    # pick out the lines in motion file corresponding to collision times
    current_line_index = 0
    for current_time in time:
        while not current_time == motionFile[current_line_index][1]:
            current_line_index += 1
        currentLine = motionFile[current_line_index]
        obj_glob = np.array([float(currentLine[2]), float(
            currentLine[3]), float(currentLine[4])])
        rotation_matrix = np.array([[float(currentLine[5]), float(currentLine[6]), float(currentLine[7])],
                                    [float(currentLine[8]), float(
                                        currentLine[9]), float(currentLine[10])],
                                    [float(currentLine[11]), float(currentLine[12]), float(currentLine[13])]])
        diff = campos_glob - obj_glob
        campos = np.dot(diff, rotation_matrix)
        campos_obj.append(campos)

    #impulseMag = [x/max_impulse for x in impulseMag]

    allVertices = np.array([0, 0, 0])
    vertexCounter = 0
    triangleCounter = 0
    dist = [(float('Inf'), vertexCounter)] * len(time)
    vertexDict = {}
    surfaceDict = {}

    readMesh = open(objFile, "r")
    while (True):
        newLine = readMesh.readline().split()
        if len(newLine) == 0:
            break
        if newLine[0] == "v":
            assert (len(newLine) == 4), "Incorrect file format"
            vertexCoord = np.array(
                [float(newLine[1]), float(newLine[2]), float(newLine[3])])
            newDist = np.linalg.norm(collisionPoint - vertexCoord, axis=1)
            vertexCounter += 1
            allVertices = np.vstack((allVertices, vertexCoord))
            for i in range(len(dist)):
                if newDist[i] < dist[i][0]:
                    dist[i] = (newDist[i], vertexCounter)
        elif newLine[0] == "f":
            assert (len(newLine) == 4), "Incorrect file format"
            vtx1, vtx2, vtx3 = int(newLine[1]), int(
                newLine[2]), int(newLine[3])
            surfaceDict[triangleCounter] = [vtx1, vtx2, vtx3]
            if vtx1 in vertexDict:
                vertexDict[vtx1].append(triangleCounter)
            else:
                vertexDict[vtx1] = [triangleCounter]
            if vtx2 in vertexDict:
                vertexDict[vtx2].append(triangleCounter)
            else:
                vertexDict[vtx2] = [triangleCounter]
            if vtx3 in vertexDict:
                vertexDict[vtx3].append(triangleCounter)
            else:
                vertexDict[vtx3] = [triangleCounter]
            triangleCounter += 1
        else:
            continue
    allVertices = np.delete(allVertices, 0, 0)
    print(allVertices.shape)
    readMesh.close()

    result = []
    for i, eachPoint in enumerate(dist):
        pointCoord = collisionPoint[i]
        surfaceId = vertexDict[eachPoint[1]]
        nearest = (float('Inf'), 0)
        for eachId in surfaceId:
            vertices = surfaceDict[eachId]
            vtx1 = allVertices[vertices[0] - 1]
            vtx2 = allVertices[vertices[1] - 1]
            vtx3 = allVertices[vertices[2] - 1]
            distance = getDistance(pointCoord, vtx1, vtx2, vtx3)
            if distance < nearest[0]:
                nearest = (distance, eachId)
        result.append(nearest[1])

    writeFileOut = open(fileOut, "w")
    writeFileOut.write("time = ")
    for i in time:
        writeFileOut.write("%s " % i)
    writeFileOut.write("\nID = ")
    for i in result:
        writeFileOut.write("%d " % i)
    writeFileOut.write("\namplitude = ")
    for i in impulseMag:
        writeFileOut.write("%s " % i)
    writeFileOut.write("\nnorm1 = ")
    for i in impulseNormalX:
        writeFileOut.write("%s " % i)
    writeFileOut.write("\nnorm2 = ")
    for i in impulseNormalY:
        writeFileOut.write("%s " % i)
    writeFileOut.write("\nnorm3 = ")
    for i in impulseNormalZ:
        writeFileOut.write("%s " % i)
    writeFileOut.write("\ncamX = ")
    for i in campos_obj:
        writeFileOut.write("%s " % i[0])
    writeFileOut.write("\ncamY = ")
    for i in campos_obj:
        writeFileOut.write("%s " % i[1])
    writeFileOut.write("\ncamZ = ")
    for i in campos_obj:
        writeFileOut.write("%s " % i[2])

    writeFileOut.write("\n")
    writeFileOut.close()

print("Generating non-filtered version.")
for ID in ID2index:
    index = ID2index[ID]
    objFile = ID2obj[ID]
    collisionFile = collisionFiles[index]
    motionFile = motionFiles[index]
    fileOut = "collision_output-" + str(ID) + "_nofilter.dat"

    time = []
    collisionPoint = np.array([0.0, 0.0, 0.0])
    impulseNormalX = []
    impulseNormalY = []
    impulseNormalZ = []
    impulseMag = []

    campos_obj = []

    # read collision input file
    for currentLine in collisionFile:
        assert (len(currentLine) == 9), "Incorrect file format."
        time.append(currentLine[1])
        collisionPoint = np.vstack((collisionPoint, np.array(
            [float(currentLine[2]), float(currentLine[3]), float(currentLine[4])])))
        impulseNormalX.append(float(currentLine[5]))
        impulseNormalY.append(float(currentLine[6]))
        impulseNormalZ.append(float(currentLine[7]))
        impulseMag.append(float(currentLine[8]))

    collisionPoint = np.delete(collisionPoint, 0, 0)

    # read motion file

    # pick out the lines in motion file corresponding to collision times
    current_line_index = 0
    for current_time in time:
        while not current_time == motionFile[current_line_index][1]:
            current_line_index += 1
        currentLine = motionFile[current_line_index]
        obj_glob = np.array([float(currentLine[2]), float(
            currentLine[3]), float(currentLine[4])])
        rotation_matrix = np.array([[float(currentLine[5]), float(currentLine[6]), float(currentLine[7])],
                                    [float(currentLine[8]), float(
                                        currentLine[9]), float(currentLine[10])],
                                    [float(currentLine[11]), float(currentLine[12]), float(currentLine[13])]])
        diff = campos_glob - obj_glob
        campos = np.dot(diff, rotation_matrix)
        campos_obj.append(campos)

    #impulseMag = [x/max_impulse for x in impulseMag]

    allVertices = np.array([0, 0, 0])
    vertexCounter = 0
    triangleCounter = 0
    dist = [(float('Inf'), vertexCounter)] * len(time)
    vertexDict = {}
    surfaceDict = {}

    readMesh = open(objFile, "r")
    while (True):
        newLine = readMesh.readline().split()
        if len(newLine) == 0:
            break
        if newLine[0] == "v":
            assert (len(newLine) == 4), "Incorrect file format"
            vertexCoord = np.array(
                [float(newLine[1]), float(newLine[2]), float(newLine[3])])
            newDist = np.linalg.norm(collisionPoint - vertexCoord, axis=1)
            vertexCounter += 1
            allVertices = np.vstack((allVertices, vertexCoord))
            for i in range(len(dist)):
                if newDist[i] < dist[i][0]:
                    dist[i] = (newDist[i], vertexCounter)
        elif newLine[0] == "f":
            assert (len(newLine) == 4), "Incorrect file format"
            vtx1, vtx2, vtx3 = int(newLine[1]), int(
                newLine[2]), int(newLine[3])
            surfaceDict[triangleCounter] = [vtx1, vtx2, vtx3]
            if vtx1 in vertexDict:
                vertexDict[vtx1].append(triangleCounter)
            else:
                vertexDict[vtx1] = [triangleCounter]
            if vtx2 in vertexDict:
                vertexDict[vtx2].append(triangleCounter)
            else:
                vertexDict[vtx2] = [triangleCounter]
            if vtx3 in vertexDict:
                vertexDict[vtx3].append(triangleCounter)
            else:
                vertexDict[vtx3] = [triangleCounter]
            triangleCounter += 1
        else:
            continue
    allVertices = np.delete(allVertices, 0, 0)
    print(allVertices.shape)
    readMesh.close()

    result = []
    for i, eachPoint in enumerate(dist):
        pointCoord = collisionPoint[i]
        surfaceId = vertexDict[eachPoint[1]]
        nearest = (float('Inf'), 0)
        for eachId in surfaceId:
            vertices = surfaceDict[eachId]
            vtx1 = allVertices[vertices[0] - 1]
            vtx2 = allVertices[vertices[1] - 1]
            vtx3 = allVertices[vertices[2] - 1]
            distance = getDistance(pointCoord, vtx1, vtx2, vtx3)
            if distance < nearest[0]:
                nearest = (distance, eachId)
        result.append(nearest[1])

    writeFileOut = open(fileOut, "w")
    writeFileOut.write("time = ")
    for i in time:
        writeFileOut.write("%s " % i)
    writeFileOut.write("\nID = ")
    for i in result:
        writeFileOut.write("%d " % i)
    writeFileOut.write("\namplitude = ")
    for i in impulseMag:
        writeFileOut.write("%s " % i)
    writeFileOut.write("\nnorm1 = ")
    for i in impulseNormalX:
        writeFileOut.write("%s " % i)
    writeFileOut.write("\nnorm2 = ")
    for i in impulseNormalY:
        writeFileOut.write("%s " % i)
    writeFileOut.write("\nnorm3 = ")
    for i in impulseNormalZ:
        writeFileOut.write("%s " % i)
    writeFileOut.write("\ncamX = ")
    for i in campos_obj:
        writeFileOut.write("%s " % i[0])
    writeFileOut.write("\ncamY = ")
    for i in campos_obj:
        writeFileOut.write("%s " % i[1])
    writeFileOut.write("\ncamZ = ")
    for i in campos_obj:
        writeFileOut.write("%s " % i[2])

    writeFileOut.write("\n")
    writeFileOut.close()
