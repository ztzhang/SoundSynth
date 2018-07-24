ROOT= #Path to SoundSynth
LIBPATH=$ROOT/pre_compute/external/fmmlib3d/matlab

SOURCEPATH=${ROOT}/pre_compute/script
DATASET_NAME=final100

python ${SOURCEPATH}/Pre_Calc_EV.py $1 $2 2
cd $SOURCEPATH
CURPATH=${ROOT}/data/${DATASET_NAME}/$1/models/mat-$2
FILEGENERATORS=${ROOT}/file_generator
# export LD_PRELOAD= point this to your libiomp5 if matlab is reporting stack related error when dynamic linking.
matlab -nodisplay -nodesktop -nosplash -r "addpath('${FILEGENERATORS}');addpath('${SOURCEPATH}');addpath('${LIBPATH}'); FMMsolver('$CURPATH',0); quit"

cd $CURPATH
mkdir -p moments
cd moments
if [ -f "moments.pbuf" ]
then
    echo "FOUND!!!"
else
    GENMOMENTS=${ROOT}/modal_sound/build/bin/gen_moments
    ${GENMOMENTS} ../fastbem/input-%d.dat ../bem_result/output-%d.dat 0 59
fi
