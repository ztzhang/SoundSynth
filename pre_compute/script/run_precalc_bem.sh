ROOT=ABSPATH_TO_PROJECT_FOLDER
MATLAB=YOUR_MATLAB_PATH


SOURCEPATH=${ROOT}/pre_compute/scripts
LIBPATH=/data/vision/billf/object-properties/sound/software/fmmlib3d-1.2/matlab
DATASET_NAME=final100

python ${SOURCEPATH}/Pre_Calc_EV.py $1 $2 0
cd $SOURCEPATH
CURPATH=/data/vision/billf/object-properties/sound/sound/data/final100/$1/models/mat-$2
FILEGENERATORS=${ROOT}/file_generators
$MATLAB -nodisplay -nodesktop -nosplash -r "addpath('${FILEGENERATORS}');BEMsolver('$CURPATH',0); quit"

cd $CURPATH
mkdir -p moments
cd moments
if [ -f "moments.pbuf" ]
then
    echo "FOUND!!!"
else
    GENMOMENTS=${SOURCECODE}/modal_sound/build/bin/gen_moments
    ${GENMOMENTS} ../fastbem/input-%d.dat ../bem_result/output-%d.dat 0 59
fi
