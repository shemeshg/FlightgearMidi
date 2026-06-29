#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#include "MidiClientUtil.h"
#include "TelnetClient.h"

namespace py = pybind11;



PYBIND11_MODULE(MyLibPy, m) {
    py::class_<TelnetClient>(m, "TelnetClient")
        .def(py::init<>())
        .def("open_socket", &TelnetClient::openSocket)
        .def("get_cmd", &TelnetClient::getCmd)
        .def("stop", &TelnetClient::stop);

    py::class_<MidiClientItf, std::shared_ptr<MidiClientItf>>(m, "MidiClientItf")
        .def("testMidi", &MidiClientItf::testMidi);

    m.def("getMidiClientItf", &getMidiClientItf);
}


