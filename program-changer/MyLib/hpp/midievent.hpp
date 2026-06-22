//-define-file body hpp/midievent.cpp
//-define-file header hpp/midievent.h
//-only-file body //-
//- #include "midievent.h"
//-only-file header //-
#pragma once
//- {include-header}
#include "midieventCommon.hpp" //- #include "midieventCommon.h"

//-only-file header
//-var {PRE} "MidiEvent::"
class MidiEvent : public CommonStatic
{
public:
    //- {function} 1 1
    explicit MidiEvent(int64_t deltatime, const std::vector<BYTE> &data,
                       int portNumber, std::string &portName)
        //-only-file body
        : data(data), deltatime(deltatime), portNumber(portNumber), portName(portName)
    {
    }

    //- {fn}
    int channel() const
    //-only-file body
    {
        int i_channel = 0;
        if (msgtype() == MIDI_MSG_TYPE::MIDI_CHANNEL_MESSAGES)
        {
            constexpr int channelMask = 0xf;
            i_channel = (data[0] & channelMask) + 1;
        }
        return i_channel;
    }

    //- {function} 0 2
    const std::string commandStr() const
    //-only-file body
    {
        if (msgtype() == MIDI_MSG_TYPE::MIDI_CHANNEL_MESSAGES &&
            mapMIDI_CHANNEL_MESSAGES.count(command()) > 0)
        {

            return mapMIDI_CHANNEL_MESSAGES.at(command());
        }
        else if (msgtype() == MIDI_MSG_TYPE::MIDI_SYSTEM_MESSAGES &&
                 mapMIDI_SYSTEM_MESSAGES.count(command()) > 0)
        {
            return mapMIDI_SYSTEM_MESSAGES.at(command());
        }
        else
        {
            return "";
        }
    }

    //- {fn}
    int command() const
    //-only-file body
    {
        int l_command = 0;
        if (msgtype() == MIDI_MSG_TYPE::MIDI_CHANNEL_MESSAGES)
        {
            l_command = data[0] >> 4;
        }
        else if (msgtype() == MIDI_MSG_TYPE::MIDI_SYSTEM_MESSAGES)
        {
            l_command = data[0];
        }
        return l_command;
    }

    //- {fn}
    int data1() const
    //-only-file body
    {
        int l_data1 = 0;
        if (msgtype() == MIDI_MSG_TYPE::MIDI_CHANNEL_MESSAGES)
        {
            if (data.size() > 1)
            {
                l_data1 = data[1];
            }
        }
        return l_data1;
    }

    //- {fn}
    int data2() const
    //-only-file body
    {
        int l_data2 = 0;
        if (msgtype() == MIDI_MSG_TYPE::MIDI_CHANNEL_MESSAGES)
        {
            if (data.size() > 2)
            {
                l_data2 = data[2];
            }
        }
        return l_data2;
    }

    //- {fn}
    MIDI_MSG_TYPE msgtype() const
    //-only-file body
    {
        constexpr int sysMsgLowBound = 240;
        if (data[0] < sysMsgLowBound)
        {
            return MIDI_MSG_TYPE::MIDI_CHANNEL_MESSAGES;
        }
        else
        {
            return MIDI_MSG_TYPE::MIDI_SYSTEM_MESSAGES;
        }
    }

    //-only-file header
private:
    const std::vector<BYTE> &data;
    int64_t deltatime;

    int portNumber;
    std::string &portName;
};
