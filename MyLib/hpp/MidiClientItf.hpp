//-define-file body hpp/MidiClientItf.cpp
//-define-file header hpp/MidiClientItf.h
//-only-file body //-
//- #include "MidiClientItf.h"

//-only-file header //-
#pragma once
#include <string>
#include <vector>

//- {include-header}
#include "DataConfig.hpp" //- #include "DataConfig.h"

//-only-file header
//-var {PRE} "MidiClientItf::"
class MidiClientItf
{
public:
    virtual void startMidiClient() = 0;
    virtual std::vector<std::string>  getInPorts() = 0;
    virtual std::vector<std::string>  getOutPorts() = 0;
    virtual bool getIsTelnetDisconnectedSignal() = 0;
    virtual bool getIsTelnetRunning() = 0;
    virtual std::string sendTerminalCmd(std::string cmd) = 0;
    virtual void sendTerminalRaw(std::string cmd) = 0;
    virtual void setIsTerminalDebugMode(bool bl)  = 0;
    virtual const DataConfig getDataConfig() const = 0;
    virtual void setDataConfig(const DataConfig& cfg) = 0;    

    virtual ~MidiClientItf() = default;
};
