# Building Modal Sound

This is a more specific instruction on building the binaries used for sound synthesis and precomputation.

This code is a stripped and modified version of the [educational C++ code](https://github.com/cxzheng/ModalSound) used at SIGGRAPH 2016 Course [Physically Based Sound for Computer Animation and Virtual Environments](http://graphics.stanford.edu/courses/sound/)

## Environments

All building test is under 64-bit Ubuntu 14.04.5; currently there is no support for MacOS and Windows.

## Installing libraries and software

The tools needed for building the binaries are:

- [CMake](https://cmake.org/) 3.7.1

- [GCC](https://gcc.gnu.org/) 6.3.0

These versions are tested for building the software; there might be compatibility issues if you use a different version.

Then you need to install the following libraries:

 - [Eigen3](http://eigen.tuxfamily.org/index.php?title=Main_Page)
 
 - [Qt5](http://doc.qt.io/qt-5/qt5-intro.html)
 
 - [Boost 1.57](https://beta.boost.org/), only filesystem & system library needed
 
 - [Protobuf 2.6.0](https://github.com/google/protobuf)
 
 - [GSL](https://www.gnu.org/software/gsl/doc/html/index.html)
 
 - [MKL](https://software.intel.com/en-us/mkl)
 
 #### Installing Eigen3:
 
 Eigen3 is a header only library, so there is no building involved.
 
 1. Download Eigen3 [here](http://eigen.tuxfamily.org/index.php?title=Main_Page) and unzip it to your desired diretories.
 
 2. In `modal_sound/run_cmake.sh`, change line 14 to match your Eigen3 directory, i.e.:
      
      ` Eigen_include_dir=YOUR_EIGEN3_FOLDER/include/eigen3 `
      
 #### Installing Qt5:
 
 If you are using [Anaconda](https://www.anaconda.com/download/#macos), installing PyQt5 will automatically install Qt5 libraries for you.
 
 If not, you can follow this [installation tutorial](https://wiki.qt.io/Install_Qt_5_on_Ubuntu) and add the paths of those libraies to your system environment `LD_LIBRARY_PATH`
 
 #### Installing Boost:
 
  You can follow the installation guide [here](http://www.boost.org/doc/libs/1_61_0/more/getting_started/unix-variants.html).
  
  After installation, you need to add the paths of installed libraries to `modal_sound/run_cmake.sh`. Modify line 10 & 11 as:
  
    Boost_include_dir=YOUR_PATH_TO_BOOST_BUILD_DIR/include/boost
  
    Boost_lib_dir=YOUR_PATH_TO_BOOST_BUILD_DIR/lib
 
 #### Installing Protobuf:
 
  We only tested using Protobuf 2.6.0. You can follow [this link](https://github.com/google/protobuf/blob/master/src/README.md) for building Protobuf from source.
  
  After building protobuf, modify line 4-7 in `modal_sound/run_cmake.sh` as :
    
    Protobuf_inlude_dir=YOUR_PATH_TO_PROTOBUF_BUILD/include
    
    Protobuf_lite_lib=YOUR_PATH_TO_PROTOBUF_BUILD/lib/libprotobuf-lite.so
    
    Protobuf_lib=YOUR_PATH_TO_PROTOBUF_BUILD/lib/libprotobuf.so
    
    Protobuf_exe_dir=YOUR_PATH_TO_PROTOBUF_BUILD/bin/protoc
    
 #### Installing GSL:
 
 For Ubuntu users, you can use:
 
    sudo apt-get install libgsl0-dev
    
 Then, add the include path to `modal_sound/run_cmake.sh`. Modify line 17 as:
 
    Gsl_include=PATH_TO_YOUR_GSL_INSTALLATION/include/gsl
    
 In you use apt-get, the default path is `/usr/include/gsl`
 
 #### Installing MKL:
 
 You can follow [this link](https://software.intel.com/en-us/get-started-with-mkl-for-linux) for installing MKL.
 
 After installation, you should modify line 20 & 23 in `modal_sound/run_cmake.sh`:
 
    Mkl_lib=PATH_TO_MKL_INSTALLATION/lib/intel64
    
    Iomp5_path=PATH_TO_FOLDER_CONTAINING_LIBIOMP5

#### Building Binaries

After installing required libraries, simply do

    cd modal_sound
    
    ./run_cmake.sh
    
    cd build
    
    make
    
Depending on your compiler setup, there might be some warnings. The binaries should be built to `modal_sound/build/bin`. 

The built binaries are:
    
    extmat
    
    gen_moments
    
    click_synth

    
    
   
    
