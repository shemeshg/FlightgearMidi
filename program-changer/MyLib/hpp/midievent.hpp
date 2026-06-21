#pragma once
#include "midieventCommon.h"




class MidiEvent : public CommonStatic
{
public:
    explicit MidiEvent(double deltatime, std::vector< BYTE> &data,
                     int portNumber, std::string &portName):data(data),deltatime(deltatime),portNumber(portNumber), portName(portName){
    }

    std::vector<BYTE> &data;
    double deltatime;

    int portNumber;
    std::string &portName;


    MidiEvent(double deltatime, std::vector<BYTE> &data,
              int portNumber, std::string &portName) : data(data), deltatime(deltatime), portNumber(portNumber), portName(portName)
    {
    }

    int channel() const
    {
        int i_channel = 0;
        if (msgtype() == MIDI_MSG_TYPE::MIDI_CHANNEL_MESSAGES)
        {
            constexpr int channelMask = 0xf;
            i_channel = (data[0] & channelMask) + 1;
        }
        return i_channel;
    }

    const std::string commandStr() const
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

    int command() const
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

    int data1() const
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

    int data2() const
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

    MIDI_MSG_TYPE msgtype() const
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
};
