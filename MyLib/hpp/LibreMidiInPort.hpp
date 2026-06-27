//-define-file body hpp/LibreMidiInPort.cpp
//-define-file header hpp/LibreMidiInPort.h
//-only-file body //-
//- #include "LibreMidiInPort.h"

//-only-file header //-
#pragma once
#include <libremidi/libremidi.hpp>

//-only-file header
//-var {PRE} "LibreMidiInPort::"
class LibreMidiInPort
{
public:
     //- {function} 0 0
    LibreMidiInPort(std::string name, int idx, libremidi::midi_in midi, libremidi::input_port inPort)
    //-only-file body
        : portName(std::move(name)),
          portIdx(idx), midiIn(std::move(midi)),
          inPort{std::move(inPort)}    
    {
    }

    //- {fn}
    void open()
    //-only-file body
    {
        auto err = midiIn.open_port(inPort);

        if (err != stdx::error{})
        {
            err.throw_exception();
        }
    }

    //-only-file header
    const std::string &getPortName() const{
        return portName;
    }

    const int getPortIdx() const {
        return portIdx;
    }

    
private:
    std::string portName;
    int portIdx;
    libremidi::midi_in midiIn;
    libremidi::input_port inPort;
};