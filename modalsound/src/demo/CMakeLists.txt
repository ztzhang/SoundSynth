# find google protobuf library
find_package(Protobuf REQUIRED)
message("Protoc include path ${PROTOBUF_INCLUDE_DIR}")
message("Protoc exe path ${PROTOBUF_PROTOC_EXECUTABLE}")
message("Protoc lib path ${PROTOBUF_LIBRARIES}")

include_directories(
    ${GLUT_INCLUDE_DIR}
    ${OPENGL_INCLUDE_DIR}
    ${Boost_INCLUDE_DIR})

#if ( NOT QGLVIEWER_FRAMEWORK )
#    include_directories({QGLVIEWER_INCLUDE_DIR})
#endif ()

#  # Find includes in corresponding build directories
#  set(CMAKE_INCLUDE_CURRENT_DIR ON)
#  # Instruct CMake to run moc automatically when needed.
#  set(CMAKE_AUTORCC ON)
PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS ../protobuf/sploosh.proto)
# message("PROTO SRC: {PROTO_SRCS}")
# message("PROTO HDR: {PROTO_HDRS}")
# message("{PROTOBUF_LIBRARY}")

add_exe(click_synth
    ClickSoundSynth.cpp
    AudioProducer.h     AudioProducer.cpp
    ../modal/ModalModel.h
    ../modal/ModalModel.cpp
    ../transfer/FMMTransferEval.h
    ../transfer/FMMTransferEval.cpp
    ../io/MatrixIO.hpp
    ../io/MatrixIO.cpp
    ../generic/precision_type.hpp
    ../generic/precision_type.cpp
    ${PROTO_HDRS}   ${PROTO_SRCS}
    LINK_LIBRARIES  Qt5::Core   Qt5::Widgets
                    Qt5::Xml    Qt5::OpenGL
                    Qt5::Multimedia
                    ${MKL_LIBS}
                    iomp5
                    ${PROTOBUF_LIBRARY}
                    ${Boost_FILESYSTEM_LIBRARY}
                    ${Boost_SYSTEM_LIBRARY}
                    ${GSL_LIBRARIES}
    OUT_DIR ${BIN_DIR}
)
