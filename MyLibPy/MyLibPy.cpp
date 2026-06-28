#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#include "MidiClientUtil.h"

namespace py = pybind11;

void test_midi() {
    auto midiItf = getMidiClientItf();
    midiItf->testMidi();
}

PYBIND11_MODULE(MyLibPy, m) {
    m.doc() = "pybind11 MyLibPy plugin";

    m.def("test_midi", &test_midi,
          py::call_guard<py::gil_scoped_release>(),
          "test midi");
}
