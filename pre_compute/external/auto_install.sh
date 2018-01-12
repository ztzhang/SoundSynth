#!/bin/bash

# install nihu
# MATLAB_PATH=YOUR_MATLAB_PATH

git clone -b release_1.1 git://last.hit.bme.hu/toolbox/nihu.git
cd nihu/
mkdir build
cd build
cmake ../src -DNIHU_INSTALL_DIR="../bin" -DNIHU_MATLAB_PATH=$MATLAB_PATH
make
make install
cd ../../

# install libfmm3d
git clone https://github.com/zgimbutas/fmmlib3d.git
sudo apt-get install bison flex octave liboctave-dev
cd fmmlib3d/
make test
