//-define-file body hpp/MidiClient.cpp
//-define-file header hpp/MidiClient.h
//-only-file body //-
//- #include "MidiClient.h"

#include <algorithm>
#include <cmath>
#include <string>
#include <iostream>

//-only-file header //-
#pragma once
#include <libremidi/libremidi.hpp>

//- {include-header}
#include "MidiClientItf.hpp" //- #include "MidiClientItf.h"
//- {include-header}
#include "LibreMidiInPort.hpp" //- #include "LibreMidiInPort.h"
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
                            puller.callback(puller.fgKetPath, pullVal);
                        }                        
                    }
                    
                    std::this_thread::sleep_for(std::chrono::milliseconds(500));
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
    const DataConfig getDataConfig()  const override
    //-only-file body
    {
        return dataConfig;
    }

    //- {fn}
    void setDataConfig(const DataConfig& cfg) override
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
        const auto& ports = obs.get_input_ports();

        names.reserve(ports.size());

        std::transform(
            ports.begin(),
            ports.end(),
            std::back_inserter(names),
            [](const libremidi::input_port& port)
            {
                return port.display_name;
            }
        );

        return names;
    }

    //- {fn}
    std::vector<std::string>  getOutPorts() override
    //-only-file body
    {
        std::vector<std::string> names;
        const auto& ports = obs.get_output_ports();

        names.reserve(ports.size());

        std::transform(
            ports.begin(),
            ports.end(),
            std::back_inserter(names),
            [](const libremidi::output_port& port)
            {
                return port.display_name;
            }
        );

        return names;        
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

    //- {fn}
    void startMidiClient() override
    //-only-file body
    {
        
        telnetDisconnected = false;
        telnetClient.stop();
        if (!telnetClient.openSocket(dataConfig.telnetHost, dataConfig.telnetPort))
        {
            std::cout << "Telnet server - could not connect!" << std::endl;
            return;
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
                return;
            }

            // For now midiInput by copy until config moved to class variarble
            auto my_callback = [this, &midiInput](const libremidi::message &message)
            {
                for (const auto &dataConfigFromMidiToTelnet : midiInput.dataConfigFromMidiToTelnets)
                {

                    if (dataConfigFromMidiToTelnet.midiMsgType == MidiMsgType::CONTROL_CHANGE &&
                        message.get_message_type() == libremidi::message_type::CONTROL_CHANGE &&
                        (dataConfigFromMidiToTelnet.midiChannel == -1 ||
                         dataConfigFromMidiToTelnet.midiChannel == message.get_channel()) &&
                        message.bytes[1] == dataConfigFromMidiToTelnet.notePitchOrCcChannel)
                    {
                        double val = translateClamped(message.bytes[2], dataConfigFromMidiToTelnet.fromStart,
                                                      dataConfigFromMidiToTelnet.fromEnd, dataConfigFromMidiToTelnet.toStart, dataConfigFromMidiToTelnet.toEnd);
                        telnetClient.setValue(dataConfigFromMidiToTelnet.setCmd, this->formatN(val, 3));
                    }
                }
            };

            libremidi::midi_in midi{
                libremidi::input_configuration{.on_message = my_callback}};

            LibreMidiInPort lmip{std::move(midiInputName), midiInputIdx, std::move(midi), std::move(port.value())};
            lmip.open();
            libreMidiInPorts.push_back(std::move(lmip));
        }
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

    //-only-file header
private:
    std::atomic<bool> telnetDisconnected = false;
    libremidi::observer obs;

    std::vector<LibreMidiInPort> libreMidiInPorts;
    TelnetClient telnetClient;
    DataConfig dataConfig{};



    //-only-file header
};
