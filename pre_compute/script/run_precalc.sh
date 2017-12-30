SOURCECODE=/data/vision/billf/object-properties/sound
SOURCEPATH=/data/vision/billf/object-properties/sound/sound/script
LIBPATH=/data/vision/billf/object-properties/sound/software/fmmlib3d-1.2/matlab

HOSTNAME=hostname
python /data/vision/billf/object-properties/sound/sound/script/Pre_Calc_EV.py $1 $2 0 $HOSTNAME
echo finished calling
#echo $2
cd $SOURCEPATH
MATLAB=/afs/csail.mit.edu/common/matlab/2015a/bin/matlab
CURPATH=/data/vision/billf/object-properties/sound/sound/data/final100/$1/models/mat-$2
$MATLAB -nodisplay -nodesktop -nosplash -r "addpath('${SOURCEPATH}');addpath('${LIBPATH}'); FMMsolver('$CURPATH',0); quit"

cd $CURPATH
mkdir -p moments
cd moments
if [ -f "moments.pbuf" ]
then
    echo "FOUND!!!"
else
    GENMOMENTS=${SOURCECODE}/sound/code/ModalSound/build/bin/gen_moments
    ${GENMOMENTS} ../fastbem/input-%d.dat ../bem_result/output-%d.dat 0 59
fi
