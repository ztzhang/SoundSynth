#!/bin/bash
# Path to your MKL Library. should look like SOMEPATH/mkl/lib/intel64
export Mkl_lib=YOUR_PATH_TO_MKL_LIB

#Path to the folder containing libiomp5.so
export Iomp5_path=PATH_TO_IOMP5_FOLDER

#Path to your matlab installation
export MATLAB_PATH=YOUR_MATLAB_INSTALL_PATH

PROJECT_PATH=$('pwd')

#modal sound
cd modal_sound
./auto_install.sh

# bullet
cd $PROJECT_PATH
cd bullet3/build3
./premake4_linux64 gmake
cd gmake
make App_RigidBodyFromObjExampleGui

# Precompute
cd $PROJECT_PATH
cd pre_compute/external
./auto_install.sh
