//-define-file body hpp/DataConfig.cpp
//-define-file header hpp/DataConfig.h
//-only-file body //-
//- #include "DataConfig.h"

//-only-file header //-
#pragma once
#include <string>
#include <vector>
#include <functional>


enum class MidiMsgType : uint8_t
{
    INVALID = 0x0,
    // Standard Message
    NOTE_OFF = 0x80,
    NOTE_ON = 0x90,
    POLY_PRESSURE = 0xA0,
    CONTROL_CHANGE = 0xB0,
    PROGRAM_CHANGE = 0xC0,
    AFTERTOUCH = 0xD0,
    PITCH_BEND = 0xE0,

    // System Common Messages
    SYSTEM_EXCLUSIVE = 0xF0,
    TIME_CODE = 0xF1,
    SONG_POS_POINTER = 0xF2,
    SONG_SELECT = 0xF3,
    RESERVED1 = 0xF4,
    RESERVED2 = 0xF5,
    TUNE_REQUEST = 0xF6,
    EOX = 0xF7,

    // System Realtime Messages
    TIME_CLOCK = 0xF8,
    RESERVED3 = 0xF9,
    START = 0xFA,
    CONTINUE = 0xFB,
    STOP = 0xFC,
    RESERVED4 = 0xFD,
    ACTIVE_SENSING = 0xFE,
    SYSTEM_RESET = 0xFF
};

class DataConfigFromMidiToTelnet
{
public:
    double fromStart = 0, fromEnd = 127, toStart = 0, toEnd = 1;
    MidiMsgType midiMsgType = MidiMsgType::INVALID;
    int midiChannel = -1;
    int notePitchOrCcChannel = 0;
    std::string setCmd;
};

class DataConfigMidiInput
{
public:
    std::string midiInputName;
    int midiInputIdx;
    std::vector<DataConfigFromMidiToTelnet> dataConfigFromMidiToTelnets;
};

class DataConfigPullerFgKey
{
    public:
    std::string fgKetPath;
    std::function<void(std::string,std::string)> callback = [](std::string key ,std::string val){
    };

};

class DataConfig
{
public:
    std::string telnetHost;
    std::string telnetPort;
    std::vector<DataConfigMidiInput> dataConfigMidiInputs;
    std::vector<DataConfigPullerFgKey> dataConfigPullerFgKeys;
};
