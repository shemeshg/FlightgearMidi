//-define-file body hpp/MidiClientItf.cpp
//-define-file header hpp/MidiClientItf.h
//-only-file body //-
//- #include "MidiClientItf.h"

//-only-file header //-
#pragma once
#include <string>

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
    virtual std::string sendTerminalCmd(std::string cmd) = 0;
    virtual void sendTerminalRaw(std::string cmd) = 0;
    virtual void setIsTerminalDebugMode(bool bl)  = 0;

    virtual ~MidiClientItf() = default;
};
