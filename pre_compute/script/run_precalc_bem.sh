ROOT= # PATH to SoundSynth
LIBPATH=$ROOT/pre_compute/external/nihu

SOURCEPATH=${ROOT}/pre_compute/script
DATASET_NAME=final100

python ${SOURCEPATH}/Pre_Calc_EV.py $1 $2 1
cd $SOURCEPATH
CURPATH=$ROOT/data/$DATASET_NAME/$1/models/mat-$2
FILEGENERATORS=${ROOT}/file_generator
matlab -nodisplay -nodesktop -nosplash -r "addpath('${FILEGENERATORS}');addpath('${LIBPATH}/bin/matlab');addpath('${LIBPATH}/bin/tutorial');run install.m;BEMsolver('$CURPATH',0); quit"

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
