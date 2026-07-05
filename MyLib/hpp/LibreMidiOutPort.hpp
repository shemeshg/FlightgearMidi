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

    //- {fn}
    void sendNoteOn(int channel, int note, int velocity)
    //-only-file body
    {
        midiOut.send_message(libremidi::channel_events::note_on(channel, note, velocity));
    }

    //- {fn}
    void sendNoteOff(int channel, int note, int velocity)
    //-only-file body
    {
        midiOut.send_message(libremidi::channel_events::note_off(channel, note, velocity));
    }

    //- {fn}
    void sendControlChange(int channel, int control, int value)
    //-only-file body
    {
        midiOut.send_message(libremidi::channel_events::control_change(channel, control, value));
    }

    //-only-file header
    const std::string &getPortName() const
    {
        return portName;
    }

    const int getPortIdx() const
    {
        return portIdx;
    }

    const int getIsOpened() const
    {
        return isOpened;
    }


private:
    bool isOpened = false;
    std::string portName;
    int portIdx;
    libremidi::midi_out midiOut;
    libremidi::output_port outPort;
};