# [[[cog
# import cog
# from CMakeCog import getCmake
# cog.outl(getCmake())
# ]]]

SET(GEN_HPP TRUE)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
if(GEN_HPP)    
                               
    make_directory(${CMAKE_CURRENT_BINARY_DIR}/hpp)


    set(HPP_GEN_FILES
        ${CMAKE_SOURCE_DIR}/scripts/hppTemplates.txt
        ${CMAKE_CURRENT_SOURCE_DIR}/hpp/DataConfig.hpp
${CMAKE_CURRENT_SOURCE_DIR}/hpp/HttpdClient.hpp
${CMAKE_CURRENT_SOURCE_DIR}/hpp/LibreMidiInPort.hpp
${CMAKE_CURRENT_SOURCE_DIR}/hpp/LibreMidiOutPort.hpp
${CMAKE_CURRENT_SOURCE_DIR}/hpp/MidiClient.hpp
${CMAKE_CURRENT_SOURCE_DIR}/hpp/MidiClientItf.hpp
${CMAKE_CURRENT_SOURCE_DIR}/hpp/MidiClientUtil.hpp
${CMAKE_CURRENT_SOURCE_DIR}/hpp/TelnetClient.hpp
    )
    add_custom_target(runScript_b64fa7459a21b0f2b87477be85ed5180eac925e48113d35950b36e2777daa950 ALL
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/parseHpp.py ${HPP_GEN_FILES}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Running parseHpp shell script")

    # Run a shell script before everything else
    execute_process(
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/parseHpp.py ${HPP_GEN_FILES}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        RESULT_VARIABLE result
    )

    # Check the result of the script execution
    if(NOT result EQUAL 0)
        message(FATAL_ERROR "Script execution failed with result: ${result}")
    endif()

    # Continue with the rest of your CMake configuration
endif()
                     

include(FetchContent)
FetchContent_Declare(
    libremidi
    GIT_REPOSITORY https://github.com/celtera/libremidi
    GIT_TAG        master
)
FetchContent_MakeAvailable(libremidi)
FetchContent_Declare(
    sigslot
    GIT_REPOSITORY https://github.com/palacaze/sigslot
    GIT_TAG        master
)
FetchContent_MakeAvailable(sigslot)
FetchContent_Declare(
    cpr
    GIT_REPOSITORY https://github.com/libcpr/cpr.git
    GIT_TAG        master
)
FetchContent_MakeAvailable(cpr)
add_library(MyLib STATIC    
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/DataConfig.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/DataConfig.h
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/HttpdClient.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/HttpdClient.h
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/LibreMidiInPort.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/LibreMidiInPort.h
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/LibreMidiOutPort.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/LibreMidiOutPort.h
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/MidiClient.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/MidiClient.h
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/MidiClientItf.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/MidiClientItf.h
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/MidiClientUtil.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/MidiClientUtil.h
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/TelnetClient.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/TelnetClient.h
    ${CMAKE_CURRENT_SOURCE_DIR}/hpp/DataConfig.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/hpp/HttpdClient.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/hpp/LibreMidiInPort.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/hpp/LibreMidiOutPort.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/hpp/MidiClient.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/hpp/MidiClientItf.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/hpp/MidiClientUtil.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/hpp/TelnetClient.hpp
    )
set_target_properties(MyLib PROPERTIES LINKER_LANGUAGE CXX)

target_link_libraries(MyLib PUBLIC libremidi)
target_link_libraries(MyLib PUBLIC Pal::Sigslot)
target_link_libraries(MyLib PUBLIC cpr::cpr)
target_include_directories(MyLib PUBLIC ${CMAKE_CURRENT_BINARY_DIR}/hpp)

if(GEN_HPP)
  add_dependencies(MyLib runScript_b64fa7459a21b0f2b87477be85ed5180eac925e48113d35950b36e2777daa950)
endif()
        
# [[[end]]]