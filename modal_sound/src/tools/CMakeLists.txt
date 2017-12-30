add_executable(extmat
    extract_matrices.cpp
    ../sc/PardisoMatrix.hpp        ../sc/PardisoMatrix.cpp
    ../deformable/stvk.h           ../deformable/stvk.cpp
    ../generic/precision_type.hpp  ../generic/precision_type.cpp)
target_link_libraries(extmat
    ${MKL_LIBS} -liomp5 ${CMAKE_THREAD_LIBS_INIT})
set_target_properties(extmat 
    PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${BIN_DIR})
