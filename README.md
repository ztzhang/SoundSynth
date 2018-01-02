# SoundSynth

This repository contains sound synthesis code used by our papers:

* [Generative Modeling of Audible Shapes for Object Perception](http://sound.csail.mit.edu/papers/gensound_iccv.pdf)

* [Shape and Material from Sound](http://sound.csail.mit.edu/papers/fastsound_nips.pdf)

 Project page:  [http://sound.csail.mit.edu/](http://sound.csail.mit.edu/)
 
 # Environment & prerequisities:
 
 Our code is only tested on 64-bit Ubuntu 14.04.5.
 
 The code need the following softwares and libraries to build :
 
 - GCC 6.3.0
 
 - CMake 3.7.1
 
 - Eigen3
 
 - QT5
 
 - Protobuf 2.6.0
 
 - GSL
 
 - MKL
 
 # Usage:
 
 The code is structured as two seperate parts: **offline pre-compuation** and **online synthesis**
 
  ### offline pre-computation:
  
  The input to pre-computation is a tetrahedron mesh, one can conver an ordinary mesh into it using [TetGen](http://wias-berlin.de/software/tetgen/) or [IsoStuffer](https://github.com/cxzheng/ModalSound) described by [Labelle and Shewchuk 2007](http://www.cs.berkeley.edu/~jrs/papers/stuffing.pdf).
  
  #### building **Modal Sound**
  
  1. modify **modal_sound/run_cmake.sh** to provide directories to required libraries and include files.
  
  2. run `./run_cmake.sh`
  
  3. enter **modal_sound/build** and run `make`
  
  
  
  
 
  ### online synthesis:
 
 The online synthesis part use [bullet](https://github.com/bulletphysics/bullet3) for physical simulation and a modified version of [Modal Sound Synthesis](https://github.com/cxzheng/ModalSound) for sound synthesis.
 
  #### Building **Bullet**
  
  1. enter **Bullet3/build3**
  
  2. run `premake_linux64 gmake`
  
  3. enter gmake, run `make App_RigidBodyFromObjExampleGui`
  
  4. The built binary is located in **bullet3/bin**
  
  If you need to modify our simulation code, they are located in **bullet3/modified_scripts**
  
  

  
  


 
 
 
