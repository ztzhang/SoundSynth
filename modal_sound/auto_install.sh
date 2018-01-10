#!/bin/bash
#MKL_PATH
export Mkl_lib=/data/vision/billf/object-properties/sound/software/mkl/mkl/lib/intel64/

#Iomp5 path
export Iomp5_path=/data/vision/billf/object-properties/sound/software/lib




# install Qt5
sudo apt-get install qt5-default qttools-dev-tools

# install Gsl
sudo apt-get install libgsl0-dev

#install eigen
cd external
if [ ! -d "./Eigen3" ]; then
    echo 'installing protobuf from current build'
    wget http://bitbucket.org/eigen/eigen/get/3.3.4.tar.gz -O Eigen3.3.4.tar.gz
    tar -xvf Eigen3.3.4.tar.gz
    rm Eigen3.3.4.tar.gz
    mv eigen* ./Eigen3
    cd ..
fi
cd ..
#install Boost
sudo apt-get install libboost-all-dev

#install protobuf
mkdir -p external
cd external
if [ ! -d "./protobuf-master/build" ]; then
    echo 'installing protobuf from current build'
    wget https://github.com/google/protobuf/archive/master.zip -O protobuf.zip
    unzip protobuf.zip
    cd protobuf-master
    ./autogen.sh
    ./configure --prefix=$('pwd')/build
    make -j
    make check -j
    make install
    cd ..
fi
cd ..

#define path Vatiables:
export Protobuf_inlude_dir=$('pwd')/external/protobuf-master/build/include
export Protobuf_lite_lib=$('pwd')/external/protobuf-master/build/lib/libprotobuf-lite.so
export Protobuf_lib=$('pwd')/external/protobuf-master/build/lib/libprotobuf.so
export Protoc_exe_dir=$('pwd')/external/protobuf-master/build/bin/protoc

#Boost
export Boost_include_dir=/usr/include/boost
export Boost_lib_dir=/usr/lib/x86_64-linux-gnu

#Eigen
export Eigen_include_dir=$('pwd')/external/Eigen3

#GSL
export Gsl_include=/usr/include/gsl

echo $Gsl_include

./run_cmake.sh
