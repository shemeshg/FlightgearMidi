add_library(MyLib STATIC
    TelnetClient.cpp
)
set_target_properties(MyLib PROPERTIES LINKER_LANGUAGE CXX)

target_include_directories(MyLib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})