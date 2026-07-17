//-define-file body hpp/MidiClient.cpp
//-define-file header hpp/MidiClient.h
//-only-file body //-
//- #include "MidiClient.h"

#include <algorithm>
#include <cmath>
#include <string>
#include <iostream>
#include <unordered_map>

//-only-file header //-
#pragma once
#include <libremidi/libremidi.hpp>

//- {include-header}
#include "MidiClientItf.hpp" //- #include "MidiClientItf.h"
//- {include-header}
#include "LibreMidiInPort.hpp" //- #include "LibreMidiInPort.h"
//- {include-header}
#include "LibreMidiOutPort.hpp" //- #include "LibreMidiOutPort.h"
//- {include-header}
#include "TelnetClient.hpp" //- #include "TelnetClient.h"
//- {include-header}
#include "DataConfig.hpp" //- #include "DataConfig.h"

//-only-file header
//-var {PRE} "MidiClient::"
class MidiClient : public MidiClientItf
{
public:
    //- {function} 0 1
    explicit MidiClient()
    //-only-file body
    {
        telnetClient.sigIsRunningChanged.connect([this](bool isRunning)
                                                 {
            if (isRunning == false){
            std::cerr << "[MAIN] Telnet disconnected, restart requested...\n";
            this->telnetDisconnected = true;
            } });

        std::thread worker([this]()
                           {
            while (true) {                
                if(telnetClient.isRunning()){
                    if (!telnetClient.getIsTerminalDebugMode()){
                        for(const auto &puller: dataConfig.dataConfigPullerFgKeys){                            
                            std::string pullVal = telnetClient.getValue(puller.fgKetPath);
                            if (isPullerUnoderedMapValueChanged(puller.fgKetPath, pullVal)){
                                puller.callback(puller.fgKetPath, pullVal);
                            }
                            if (pullerSleepInterval != 0){
                                std::this_thread::sleep_for(std::chrono::milliseconds(pullerSleepInterval));
                            }                            
                        }                        
                    }
                    

                    
                }

            } });
        worker.detach();
    }

    //- {fn}
    void setIsTerminalDebugMode(bool bl) override
    //-only-file body
    {
        telnetClient.setIsTerminalDebugMode(bl);
    }

    //- {fn}
    void sendTerminalRaw(std::string cmd) override
    //-only-file body
    {
        if (telnetClient.isRunning())
        {
            telnetClient.sendTerminalRaw(cmd);
        }
    }

    //- {fn}
    std::string sendTerminalCmd(std::string cmd) override
    //-only-file body
    {
        if (telnetClient.isRunning())
        {
            return telnetClient.getCmd(cmd);
        }
        else
        {
            return "";
        }
    }

    //- {function} 0 2
    const DataConfig getDataConfig() const override
    //-only-file body
    {
        return dataConfig;
    }

    //- {fn}
    void setDataConfig(const DataConfig &cfg) override
    //-only-file body
    {
        dataConfig = cfg;
    }

    //- {fn}
    bool getIsTelnetRunning() override
    //-only-file body
    {
        return telnetClient.isRunning();
    }

    //- {fn}
    bool getIsTelnetDisconnectedSignal() override
    //-only-file body
    {
        return telnetDisconnected;
    }

    //- {fn}
    std::vector<std::string> getInPorts() override
    //-only-file body
    {
        std::vector<std::string> names;
        const auto &ports = obs.get_input_ports();

        names.reserve(ports.size());

        std::transform(
            ports.begin(),
            ports.end(),
            std::back_inserter(names),
            [](const libremidi::input_port &port)
            {
                return port.display_name;
            });

        return names;
    }

    //- {fn}
    std::vector<std::string> getOutPorts() override
    //-only-file body
    {
        std::vector<std::string> names;
        const auto &ports = obs.get_output_ports();

        names.reserve(ports.size());

        std::transform(
            ports.begin(),
            ports.end(),
            std::back_inserter(names),
            [](const libremidi::output_port &port)
            {
                return port.display_name;
            });

        return names;
    }

    //- {fn}
    LibreMidiOutPort *getLibreMidiOutPort(std::string midiOutputName, int midiOutputIdx) override
    //-only-file body
    {
        auto it = std::find_if(
            libreMidiOutPorts.begin(),
            libreMidiOutPorts.end(),
            [midiOutputIdx, &midiOutputName](const LibreMidiOutPort &port)
            {
                return port.getPortIdx() == midiOutputIdx &&
                       port.getPortName() == midiOutputName;
            });

        if (it == libreMidiOutPorts.end())
        {
            throw std::runtime_error("Out Port not found");
        }

        return &*it; // return reference to existing object
    }

    //- {fn}
    bool openLibreMidiOutPort(std::string midiOutputName, int midiOutputIdx) override
    //-only-file body
    {
        auto it = std::find_if(
            libreMidiOutPorts.begin(),
            libreMidiOutPorts.end(),
            [midiOutputIdx, &midiOutputName](const LibreMidiOutPort &port)
            {
                return port.getPortIdx() == midiOutputIdx &&
                       port.getPortName() == midiOutputName;
            });

        if (it == libreMidiOutPorts.end())
        {
            auto port = getOutPortByName(midiOutputName, midiOutputIdx);
            if (port)
            {
                std::cout << "Found port: " << port->display_name << std::endl;
            }
            else
            {
                std::cout << "Port not found!" << std::endl;
                return false;
            }

            libremidi::midi_out midi{
                libremidi::output_configuration{}};

            LibreMidiOutPort lmop{std::move(midiOutputName), midiOutputIdx, std::move(midi), std::move(port.value())};
            lmop.open();
            libreMidiOutPorts.push_back(std::move(lmop));
        }

        return true;
    }

    //- {fn}
    bool startMidiClient() override
    //-only-file body
    {

        telnetDisconnected = false;
        telnetClient.stop();
        telnetClient.telnetInitCmds = dataConfig.telnetInitCmds;
        if (!telnetClient.openSocket(dataConfig.telnetHost, dataConfig.telnetPort))
        {
            std::cout << "Telnet server - could not connect!" << std::endl;
            return false;
        }

        libreMidiInPorts.clear();
        for (const auto &midiInput : dataConfig.dataConfigMidiInputs)
        {
            std::string midiInputName = midiInput.midiInputName;
            int midiInputIdx = midiInput.midiInputIdx;
            auto port = getInPortByName(midiInputName, midiInput.midiInputIdx);
            if (port)
            {
                std::cout << "Found port: " << port->display_name << std::endl;
            }
            else
            {
                std::cout << "Port not found!" << std::endl;
                return false;
            }

            // For now midiInput by copy until config moved to class variarble
            auto my_callback = [this, &midiInput](const libremidi::message &message)
            {
                for (const auto &dataConfigFromMidiToTelnet : midiInput.dataConfigFromMidiToTelnets)
                {
                    if (dataConfigFromMidiToTelnet->midiMsgType == static_cast<MidiMsgType>(message.get_message_type()) &&
                        (dataConfigFromMidiToTelnet->midiChannel == -1 ||
                         dataConfigFromMidiToTelnet->midiChannel == message.get_channel()) &&
                        message.bytes[1] == dataConfigFromMidiToTelnet->notePitchOrCcChannel)
                    {
                        if (dataConfigFromMidiToTelnet->isCallback)
                        {

                            std::vector<int> raw;
                            raw.reserve(message.bytes.size());

                            for (unsigned char b : message.bytes)
                                raw.push_back(static_cast<int>(b));

                            dataConfigFromMidiToTelnet->callback(raw);
                        }
                        else
                        {
                            double val = translateClamped(message.bytes[2], dataConfigFromMidiToTelnet->fromStart,
                                                          dataConfigFromMidiToTelnet->fromEnd, dataConfigFromMidiToTelnet->toStart, dataConfigFromMidiToTelnet->toEnd);
                            telnetClient.setValue(dataConfigFromMidiToTelnet->setCmd, this->formatN(val, 3));
                        }
                    }
                }
            };

            libremidi::midi_in midi{
                libremidi::input_configuration{.on_message = my_callback}};

            LibreMidiInPort lmip{std::move(midiInputName), midiInputIdx, std::move(midi), std::move(port.value())};
            lmip.open();
            libreMidiInPorts.push_back(std::move(lmip));
        }
        return true;
    }

    //-only-file header
private:
    std::atomic<bool> telnetDisconnected = false;
    libremidi::observer obs{
        libremidi::observer_configuration{
            .track_virtual = true}};

    std::vector<LibreMidiInPort> libreMidiInPorts;
    std::vector<LibreMidiOutPort> libreMidiOutPorts;
    TelnetClient telnetClient;
    DataConfig dataConfig{};

    std::unordered_map<std::string, std::string> pullerCashMap;

    //- {fn}
    bool isPullerUnoderedMapValueChanged(std::string key, std::string newVal)
    //-only-file body
    {
        auto it = pullerCashMap.find(key);

        if (it != pullerCashMap.end())
        {
            if (it->second != newVal)
            {
                it->second = newVal;
                return true;
            }
            return false;
        }

        pullerCashMap[key] = newVal;
        return true;
    }

    //- {fn}
    double translateClamped(double value,
                            double fromStart, double fromEnd,
                            double toStart, double toEnd)
    //-only-file body
    {
        double t = (value - fromStart) / (fromEnd - fromStart);
        t = std::clamp(t, 0.0, 1.0);
        return toStart + t * (toEnd - toStart);
    }

    //- {fn}
    std::string formatN(double x, int decimals)
    //-only-file body
    {
        double scale = std::pow(10.0, decimals);
        double r = std::round(x * scale) / scale;

        std::string s = std::to_string(r);

        // remove trailing zeros
        s.erase(s.find_last_not_of('0') + 1);

        // remove trailing decimal point
        if (!s.empty() && s.back() == '.')
            s.pop_back();

        return s;
    }

    //- {function} 0 1
    std::optional<libremidi::output_port> getOutPortByName(std::string portName, int idx = 0)
    //-only-file body
    {
        int foundItems = 0;

        for (const libremidi::output_port &port : obs.get_output_ports())
        {
            if (port.display_name == portName)
            {
                if (idx == foundItems)
                {
                    return port;
                }
                foundItems++;
            }
        }
        return std::nullopt;
    }

    //- {function} 0 1
    std::optional<libremidi::input_port> getInPortByName(std::string portName, int idx = 0)
    //-only-file body
    {
        int foundItems = 0;

        for (const libremidi::input_port &port : obs.get_input_ports())
        {
            if (port.display_name == portName)
            {
                if (idx == foundItems)
                {
                    return port;
                }
                foundItems++;
            }
        }
        return std::nullopt;
    }

    //-only-file header
};
