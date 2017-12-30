SOURCECODE=/data/vision/billf/object-properties/sound
SOURCEPATH=/data/vision/billf/object-properties/sound/sound/script
LIBPATH=/data/vision/billf/object-properties/sound/software/fmmlib3d-1.2/matlab

python /data/vision/billf/object-properties/sound/sound/script/Pre_Calc_EV.py $1 $2 0 $HOSTNAME

cd $SOURCEPATH
source ~/.bash_profile
CURPATH=/data/vision/billf/object-properties/sound/sound/data/final100/$1/models/mat-$2
FILEGENERATORS=${SOURCECODE}/sound/code/file_generators
echo callingMatlab
matlab -nodisplay -nodesktop -nosplash -r "addpath('${FILEGENERATORS}');BEMsolver('$CURPATH',0); quit"

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
