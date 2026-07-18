# [[[cog
# import cog
# from CMakeCogMain import getCmake
# cog.outl(getCmake())
# ]]]
cmake_minimum_required(VERSION 3.15.0)
project(program-changer VERSION 0.13.0 LANGUAGES C CXX)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(BUILD_SHARED_LIBS OFF)
set(CPR_USE_SYSTEM_CURL ON)

add_subdirectory(MyLib)
add_subdirectory(FlightgearMidi)
add_executable(program-changer main.cpp)

target_link_libraries(program-changer PRIVATE MyLib)    

# [[[end]]]