#!/bin/bash

# Protobuf
# Protobuf_include_dir=
# Protobuf_lite_lib=
# Protobuf_lib=
# Protoc_exe_dir=

# Boost
# Boost_include_dir=
# Boost_lib_dir=

# Eigen
# Eigen_include_dir=

# GSL
# Gsl_include=

# MKL
# Mkl_lib=

# IOMP5
# Iomp5_path=

mkdir -p build_test
cd build_test

install_prefix=$(pwd)"/bin"
cmake .. -DProtobuf_INCLUDE_DIR=$Protobuf_include_dir -DProtobuf_LITE_LIBRARY=$Protobuf_lite_lib -DBOOST_INCLUDEDIR=$Boost_include_dir -DBOOST_LIBRARYDIR=$Boost_lib_dir -DProtobuf_PROTOC_EXECUTABLE=$Protoc_exe_dir -DProtobuf_LIBRARY=$Protobuf_lib -DEIGEN_INCLUDE_DIR=$Eigen_include_dir -DGSL_INCLUDE_DIR=$Gsl_include -DMKL_LIB=$Mkl_lib -DIOMP5_PATH=$Iomp5_path -DCMAKE_INSTALL_PREFIX=$install_prefix
