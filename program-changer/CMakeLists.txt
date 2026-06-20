# [[[cog
# import cog
# from CMakeCogMain import getCmake
# cog.outl(getCmake())
# ]]]
cmake_minimum_required(VERSION 3.10.0)
project(program-changer VERSION 0.1.0 LANGUAGES C CXX)

add_subdirectory(MyLib)


add_executable(program-changer main.cpp)
target_link_libraries(program-changer PRIVATE MyLib)
# [[[end]]]