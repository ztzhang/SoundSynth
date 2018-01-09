#!/bin/bash

#Protobuf
#Protobuf_inlude_dir=/data/vision/billf/object-properties/sound/software/protobuf-2.6.0/build/include
#Protobuf_lite_lib=/data/vision/billf/object-properties/sound/software/protobuf-2.6.0/build/lib/libprotobuf-lite.so.9.0.0
#Protobuf_lib=/data/vision/billf/object-properties/sound/software/protobuf-2.6.0/build/lib/libprotobuf.so.9.0.0
#Protoc_exe_dir=/data/vision/billf/object-properties/sound/software/protobuf-2.6.0/build/bin/protoc

#Boost
#Boost_include_dir=/data/vision/billf/object-properties/local/include/boost
#Boost_lib_dir=/data/vision/billf/object-properties/local/lib

#Eigen
#Eigen_include_dir=/data/vision/billf/object-properties/sound/software/eigen3/include/eigen3

#GSL
#Gsl_include=/data/vision/billf/object-properties/sound/software/gsl-2.2

#MKL
#Mkl_lib=/data/vision/billf/object-properties/sound/software/mkl/mkl/lib/intel64/

#IOMP5
#Iomp5_path=/data/vision/billf/object-properties/sound/software/lib

mkdir -p build_test
cd build_test
install_prefix=$(pwd)"/bin"
cmake .. -DProtobuf_INCLUDE_DIR=$Protobuf_inlude_dir -DProtobuf_LITE_LIBRARY=$Protobuf_lite_lib -DBOOST_INCLUDEDIR=$Boost_include_dir -DBOOST_LIBRARYDIR=$Boost_lib_dir -DProtobuf_PROTOC_EXECUTABLE=$Protoc_exe_dir -DProtobuf_LIBRARY=$Protobuf_lib -DEIGEN_INCLUDE_DIR=$Eigen_include_dir -DGSL_INCLUDE_DIR=$Gsl_include -DMKL_LIB=$Mkl_lib -DIOMP5_PATH=$Iomp5_path -DCMAKE_INSTALL_PREFIX=$install_prefix
