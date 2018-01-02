ROOT=ABSPATH_TO_PROJECT_FOLDER
MATLAB=YOUR_MATLAB_PATH


SOURCEPATH=${ROOT}/pre_compute/scripts
LIBPATH=/data/vision/billf/object-properties/sound/software/fmmlib3d-1.2/matlab
DATASET_NAME=final100

python ${SOURCEPATH}/Pre_Calc_EV.py $1 $2 0
echo finished calling
#echo $2
cd $SOURCEPATH
CURPATH=${ROOT}/data/${DATASET_NAME}/$1/models/mat-$2
FILEGENERATORS=${ROOT}/file_generators
$MATLAB -nodisplay -nodesktop -nosplash -r "addpath('${FILEGENERATORS}');addpath('${SOURCEPATH}');addpath('${LIBPATH}'); FMMsolver('$CURPATH',0); quit"

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
