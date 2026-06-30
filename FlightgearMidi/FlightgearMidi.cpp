#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <pybind11/functional.h>
#include <iostream>
#include "MidiClientUtil.h"
#include "TelnetClient.h"

namespace py = pybind11;

// Bind the vector types FIRST
PYBIND11_MAKE_OPAQUE(std::vector<DataConfigMidiInput>);
PYBIND11_MAKE_OPAQUE(std::vector<DataConfigFromMidiToTelnet>);
PYBIND11_MAKE_OPAQUE(std::vector<DataConfigPullerFgKey>);

PYBIND11_MODULE(FlightgearMidi, m)
{
    // Expose vectors so Python can append(), index, iterate, etc.
    py::bind_vector<std::vector<DataConfigMidiInput>>(m, "DataConfigMidiInputList");
    py::bind_vector<std::vector<DataConfigFromMidiToTelnet>>(m, "DataConfigFromMidiToTelnetList");
    py::bind_vector<std::vector<DataConfigPullerFgKey>>(m, "DataConfigPullerFgKeyList");

    // TelnetClient
    py::class_<TelnetClient>(m, "TelnetClient")
        .def(py::init<>())
        .def("open_socket", &TelnetClient::openSocket)
        .def("get_cmd", &TelnetClient::getCmd)
        .def("stop", &TelnetClient::stop);

    // MidiClientItf
    py::class_<MidiClientItf, std::shared_ptr<MidiClientItf>>(m, "MidiClientItf")
        .def("getDataConfig", &MidiClientItf::getDataConfig)
        .def("setDataConfig", &MidiClientItf::setDataConfig)
        .def("startMidiClient", &MidiClientItf::startMidiClient)
        .def("getIsTelnetRunning", &MidiClientItf::getIsTelnetRunning)
        .def("getInPorts", &MidiClientItf::getInPorts)
        .def("getOutPorts", &MidiClientItf::getOutPorts)
        .def("setIsTerminalDebugMode", &MidiClientItf::setIsTerminalDebugMode)
        .def("sendTerminalRaw", &MidiClientItf::sendTerminalRaw)
        .def("getIsTelnetDisconnectedSignal", &MidiClientItf::getIsTelnetDisconnectedSignal);

    // Enum
    py::enum_<MidiMsgType>(m, "MidiMsgType")
        .value("CONTROL_CHANGE", MidiMsgType::CONTROL_CHANGE)
        .value("NOTE_ON", MidiMsgType::NOTE_ON)
        .value("NOTE_OFF", MidiMsgType::NOTE_OFF);

    // DataConfigFromMidiToTelnet
    py::class_<DataConfigFromMidiToTelnet>(m, "DataConfigFromMidiToTelnet")
        .def(py::init<>())
        .def_readwrite("fromStart", &DataConfigFromMidiToTelnet::fromStart)
        .def_readwrite("fromEnd", &DataConfigFromMidiToTelnet::fromEnd)
        .def_readwrite("toStart", &DataConfigFromMidiToTelnet::toStart)
        .def_readwrite("toEnd", &DataConfigFromMidiToTelnet::toEnd)
        .def_readwrite("midiMsgType", &DataConfigFromMidiToTelnet::midiMsgType)
        .def_readwrite("midiChannel", &DataConfigFromMidiToTelnet::midiChannel)
        .def_readwrite("notePitchOrCcChannel", &DataConfigFromMidiToTelnet::notePitchOrCcChannel)
        .def_readwrite("setCmd", &DataConfigFromMidiToTelnet::setCmd);

    // DataConfigMidiInput
    py::class_<DataConfigMidiInput>(m, "DataConfigMidiInput")
        .def(py::init<>())
        .def_readwrite("midiInputIdx", &DataConfigMidiInput::midiInputIdx)
        .def_readwrite("midiInputName", &DataConfigMidiInput::midiInputName)
        .def_readwrite("dataConfigFromMidiToTelnets", &DataConfigMidiInput::dataConfigFromMidiToTelnets);

    // DataConfigPullerFgKey
    py::class_<DataConfigPullerFgKey>(m, "DataConfigPullerFgKey")
        .def(py::init<>())
        .def_readwrite("fgKetPath", &DataConfigPullerFgKey::fgKetPath)
        .def_property(
            "callback",
            [](DataConfigPullerFgKey &self) {
                return self.callback;
            },
            [](DataConfigPullerFgKey &self, std::function<void(std::string, std::string)> cb) {
                self.callback = cb;
            }
        )
        ;


    // DataConfig
    py::class_<DataConfig>(m, "DataConfig")
        .def(py::init<>())
        .def_readwrite("telnetHost", &DataConfig::telnetHost)
        .def_readwrite("telnetPort", &DataConfig::telnetPort)
        .def_readwrite("dataConfigMidiInputs", &DataConfig::dataConfigMidiInputs)
        .def_readwrite("dataConfigPullerFgKeys", &DataConfig::dataConfigPullerFgKeys);

    // Factory
    m.def("getMidiClientItf", &getMidiClientItf);
}
