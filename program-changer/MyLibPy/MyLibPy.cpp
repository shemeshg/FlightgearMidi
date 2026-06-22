#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

int add(int i, int j) {
    return i + j;
}

PYBIND11_MODULE(MyLibPy, m) {
    py::gil_scoped_release release;

    m.doc() = "pybind11 MyLibPy plugin";

    m.def("add", &add, "A function that adds two numbers");
}

