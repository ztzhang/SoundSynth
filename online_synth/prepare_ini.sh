#!/bin/bash
PROJECT_ROOT=/data/vision/billf/object-properties/sound/ztzhang/SoundSynth

CLICKSYNTH=${PROJECT_ROOT}/modal_sound/build/bin/click_synth
echo $CLICKSYNTH
set -e
######################## Color Settings ########################
RED='\033[1;31m'
GREEN='\033[1;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
NC='\033[0m' 
################################################################

# Parsing Arguments
usage() { echo -e "${YELLOW}Usage: $0 <-n object_name> <-d density> <-i obj_id>[-A alpha=1e-7] [-B beta=5.0]${NC}" 1>&2; exit 1;}

while getopts ":n:d:i:A:B:" opt; do
    case $opt in
		n) OBJNAME=$OPTARG;;
		d) DENSITY=$OPTARG;;
		i) OBJID=$OPTARG;;
        A) ALPHA=$OPTARG;;
		B) BETA=$OPTARG;;
		\?) echo "Invalid option: -$OPTARG"
			usage;;
		:)  echo "Option -$OPTARG requires an argument."
			usage;;
    esac
done

# Setting Directories
echo ${OBJNAME}
echo hello
# Generating .ini File
echo -e "${GREEN}==>Creating Config File for Sound Generation${NC}" #| tee -a "$LOGFILE"
printf "[mesh]\n" > click_temp.ini
printf "surface_mesh = ${OBJNAME}.obj\nvertex_mapping = adddd\n\n[audio]\nuse_audio_device = false\ndevice = \nTS = 1.0\namplitude = 2.0\ncontinuous = true\n\n[gui]\ngui=false\n\n[transfer]\nmoments = moments/moments.pbuf\n\n[modal]\nshape = ${OBJNAME}.ev\ndensity = ${DENSITY}\nalpha = ${ALPHA}\nbeta = ${BETA}\nvtx_map = ${OBJNAME}.vmap\n\n[camera]\nx = 0\ny = 0\nz = 1\n\n[collisions]\n" >> click_temp.ini
cat click_temp.ini collision_output-${OBJID}.dat > click.ini
rm click_temp.ini

################################################################

# click_synth
echo -e "${GREEN}==>Generating Continuous Audio (click_synth)${NC}" #| tee -a "$LOGFILE"
${CLICKSYNTH} -platform offscreen click.ini #| tee -a "$LOGFILE"
exit 0


