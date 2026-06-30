
include(FetchContent)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG v2.12.0   # pick a stable version
)

FetchContent_MakeAvailable(pybind11)

pybind11_add_module(FlightgearMidi FlightgearMidi.cpp)
target_link_libraries(FlightgearMidi PRIVATE MyLib)  
install(TARGETS FlightgearMidi DESTINATION FlightgearMidi)