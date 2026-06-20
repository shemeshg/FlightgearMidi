# [[[cog
# import cog
# from CMakeCog import getCmake
# cog.outl(getCmake())
# ]]]

SET(GEN_HPP TRUE)
if(GEN_HPP)
    make_directory(${CMAKE_CURRENT_BINARY_DIR}/hpp)


    set(HPP_GEN_FILES
        ${CMAKE_SOURCE_DIR}/scripts/hppTemplates.txt
        ${CMAKE_CURRENT_SOURCE_DIR}/hpp/TelnetClient.hpp
    )
    add_custom_target(runScript_b64fa7459a21b0f2b87477be85ed5180eac925e48113d35950b36e2777daa950 ALL
        COMMAND python3 ${CMAKE_SOURCE_DIR}/scripts/parseHpp.py ${HPP_GEN_FILES}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Running parseHpp shell script")

    # Run a shell script before everything else
    execute_process(
        COMMAND python3 ${CMAKE_SOURCE_DIR}/scripts/parseHpp.py ${HPP_GEN_FILES}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        RESULT_VARIABLE result
    )

    # Check the result of the script execution
    if(NOT result EQUAL 0)
        message(FATAL_ERROR "Script execution failed with result: ${result}")
    endif()

    # Continue with the rest of your CMake configuration
endif()
                     

add_library(MyLib STATIC    
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/TelnetClient.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/hpp/TelnetClient.h
    )
set_target_properties(MyLib PROPERTIES LINKER_LANGUAGE CXX)

target_include_directories(MyLib PUBLIC ${CMAKE_CURRENT_BINARY_DIR}/hpp)

if(GEN_HPP)
  add_dependencies(MyLib runScript_b64fa7459a21b0f2b87477be85ed5180eac925e48113d35950b36e2777daa950)
endif()
        
# [[[end]]]