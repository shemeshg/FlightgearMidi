# [[[cog
# import cog
# from CMakeCogMain import getCmake
# cog.outl(getCmake())
# ]]]
cmake_minimum_required(VERSION 3.10.0)
project(program-changer VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_subdirectory(MyLib)
add_subdirectory(MyLibPy)
add_executable(program-changer main.cpp)

target_link_libraries(program-changer PRIVATE MyLib)    

# [[[end]]]