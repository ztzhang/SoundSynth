# SoundSynth

This repository contains sound synthesis code used by our papers:

* [Generative Modeling of Audible Shapes for Object Perception](http://sound.csail.mit.edu/papers/gensound_iccv.pdf)

* [Shape and Material from Sound](http://sound.csail.mit.edu/papers/fastsound_nips.pdf)

Project page:  [http://sound.csail.mit.edu/](http://sound.csail.mit.edu/)
 
# Auto-install

Our code has been tested on 64-bit Ubuntu 14.04.5.
 
We provide auto install scripts for all the required libraies except Matlab & MKL. You need to modify `auto_install.sh` to indicate the paths to the MKL libraries, libiomp5 (often included in an MKL install), and Matlab.
 
Then, simply run `./auto_install.sh`. This should install all the necessary components for you to synthesize sound, including
- Eigen3
- QT5
- Protobuf 2.6.0
- GSL

The script relies on GCC and CMake. We have tested it with GCC 6.3.0 and CMake 3.7.1.
 
If you prefer to install the dependencies manually (e.g., you don't have sudo access), please refer to the [following sections](#manual-installation) for customized installation and usage. 
 
# Usage
 
The code is structured as two seperate parts: **offline pre-compuation** and **online synthesis**.
 
The definition of scenes and materials are located in `config` folder.
 
### Offline pre-computation
  
The input to pre-computation is a tetrahedron mesh. One can convert an ordinary triangular mesh using [TetGen](http://wias-berlin.de/software/tetgen/) or [IsoStuffer](https://github.com/cxzheng/ModalSound) described by [Labelle and Shewchuk 2007](http://www.cs.berkeley.edu/~jrs/papers/stuffing.pdf).
  
#### Running pre-computation
  
Our pre-computation step utilizes two different solvers for calculating sound propagation: a direct BEM solver and an accelerated BEM FMM solver. In short, the direct method is faster when your mesh has small number of faces, as the FMM solver is faster and more memory efficient when the mesh has more faces. We suggest using the direct solver for meshes with less than 1000 faces. 

One can run pre-computation using the direct method via `pre_compute/run_precalc_bem.sh` or using the FMM solver via `pre_compute/run_precalc.sh`. Note that you need to pass an object id followed by a material id to the script. The data folder sctruture should be as `data/DATASET_NAME/OBJECT_ID`; all generated files would be in `data/DATASET_NAME/OBJECT_ID/MATERIAL_ID`. For example:

`./run_precalc.sh 0 1`

will pre-compute object 0 with material 1 defined in `config/material/material-1.cfg` using FMM solver. 

### Online synthesis
 
The online synthesis part use [bullet](https://github.com/bulletphysics/bullet3) for the physical simulation and a modified version of [Modal Sound Synthesis](https://github.com/cxzheng/ModalSound) for the sound synthesis.

  
#### Running online simulation
  
The entry code is `online_synth/gen_sound.py`
  
If one wish to render the corresponding video as well, you need to install [Blender](https://www.blender.org/) and specify its path in `gen_sound.py`. Also ffmepg is need if one needs to combine seperate sound tracks or rendered images into a single soundtrack / video.
  
`gen_sound.py` takes several arguments, one can use -r to skip rendering and -v to skip compining rendered images and sound tracks into a single video. One also needs to specify the scene id, the object id and material id. An example usage is

`gen_sound.py scene-id object1-id material-for-object1-id object2-id material-for-object2-id`

# Manual Installation

#### Building **Modal Sound**
  
One can run `modelsound/auto_install.sh` to install all required libraries and build all the necessary binaries.
  
If you wish to mannully install the libraries or to customize their locations, please see [this document](https://github.com/ztzhang/SoundSynth/blob/master/documents/building_modalsound.md) for a detailed description. 
  
#### Building file generators
  
1. enter `file_generators`
  
2. run `./compile_cpps.sh`
  
#### Installing BEM/FMM Solver
  
We solve the Helmholz equation related to sound propagation using a direct BEM method and an accelerated version using FMM. 
  
1. For the direct BEM method, one needs to install the [Nihu matlab library](http://last.hit.bme.hu/nihu/index.html) and specify its path in `pre_compute/run_precalc_bem.sh`.
  
2. For the FMM BEM method, one needs to install the [FMMlib3d libraries](https://cims.nyu.edu/cmcl/fmm3dlib/fmm3dlib.html) and specify its path in `pre_compute/run_precalc.sh`.
  
A auto install script is provided in `pre_compute/extertal/auto_install.sh`. Note that you need to specify your matlab installation path in the first line of `auto_install.sh`. 

 
#### Building **Bullet**
  
1. enter `Bullet3/build3`
  
2. run `premake_linux64 gmake`
  
3. enter gmake, run `make App_RigidBodyFromObjExampleGui`
  
4. The built binary is located in `bullet3/bin`
  
If you need to modify our simulation code, they are located in `bullet3/modified_scripts`
  


  
# Data
   
Object data after precomputation: To be released
   
Sound-20k (Soundtrack only, no video): To be released.
