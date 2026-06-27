//-define-file body hpp/MidiClientItf.cpp
//-define-file header hpp/MidiClientItf.h
//-only-file body //-
//- #include "MidiClientItf.h"

//-only-file header //-
#pragma once
#include <memory>

//-only-file header
//-var {PRE} "MidiClientItf::"
class MidiClientItf
{
public:
    virtual void testMidi() = 0;
    virtual void getInPorts() = 0;
    virtual void getOutPorts() = 0;
    virtual bool getIsTelnetDisconnectedSignal() = 0;
    virtual bool getIsTelnetRunning() = 0;

    virtual ~MidiClientItf() = default;
};
