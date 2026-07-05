//-define-file body hpp/LibreMidiOutPort.cpp
//-define-file header hpp/LibreMidiOutPort.h
//-only-file body //-
//- #include "LibreMidiOutPort.h"

//-only-file header //-
#pragma once
#include <libremidi/libremidi.hpp>

//-only-file header
//-var {PRE} "LibreMidiOutPort::"
class LibreMidiOutPort
{
public:
     //- {function} 0 0
    LibreMidiOutPort(std::string name, int idx, libremidi::midi_out midi, libremidi::output_port outPort)
    //-only-file body
        : portName(std::move(name)),
          portIdx(idx), midiOut(std::move(midi)),
          outPort{std::move(outPort)}    
    {
    }

    //- {fn}
    void open()
    //-only-file body
    {
        auto err = midiOut.open_port(outPort);

        if (err != stdx::error{})
        {
            err.throw_exception();
        }
        isOpened = true;
    }

    //-only-file header
    const std::string &getPortName() const{
        return portName;
    }

    const int getPortIdx() const {
        return portIdx;
    }

    const int getIsOpened() const {
        return isOpened;
    }    
    
    void test(){
        int channel = 0;
        int note=60;
        int control = 60;
        int value = 60;
        int velocity = 60;
        midiOut.send_message(libremidi::channel_events::note_on(channel, note, velocity));
        midiOut.send_message(libremidi::channel_events::control_change(channel, control, value));
    }

private:
    bool isOpened = false;
    std::string portName;
    int portIdx;
    libremidi::midi_out midiOut;
    libremidi::output_port outPort;
};