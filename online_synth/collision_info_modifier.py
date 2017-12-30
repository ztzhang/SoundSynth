
import sys
#from sets import Set

assert (len(sys.argv) == 6), "Usage: collision_info_modifier.py <collision_info.dat> <motion_info.dat> <collision.dat> <motion.dat> <collision_motion.dat>"
collisionFileIn = sys.argv[1]
motionFileIn = sys.argv[2]
collisionFileOut = sys.argv[3]
motionFileOut = sys.argv[4]
comboFileOut = sys.argv[5]


readCollision = open(collisionFileIn, "r")
writeCollision = open(collisionFileOut, "w")
firstLine = readCollision.readline()

lines = readCollision.readlines()
for line in sorted(lines, key=lambda line: line.split()[0]):
    writeCollision.write(line)
writeCollision.close()
readCollision.close()

readMotion = open(motionFileIn, "r")
writeMotion = open(motionFileOut, "w")
lines = readMotion.readlines()
for line in sorted(lines, key=lambda line: line.split()[0]):
    writeMotion.write(line)
writeMotion.close()
readMotion.close()

comboCollision = open(collisionFileOut, "r")
comboMotion = open(motionFileOut, "r")
writeCombo = open(comboFileOut, "w")

ids = set([])
writeCombo.write(firstLine)
for line in comboCollision.readlines():
    writeCombo.write(line)
    lineid = line.split()[0]
    if lineid not in ids:
        ids.add(lineid)
comboCollision.close()

for line in comboMotion.readlines():
    lineid = line.split()[0]
    if lineid in ids:
        writeCombo.write(line)
comboMotion.close()
writeCombo.close()
