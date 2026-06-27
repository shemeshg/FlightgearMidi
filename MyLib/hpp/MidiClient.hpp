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
#include <optional>

//- {include-header}
#include "MidiClientItf.hpp" //- #include "MidiClientItf.h"
//- {include-header}
#include "LibreMidiInPort.hpp" //- #include "LibreMidiInPort.h"
//- {include-header}
#include "TelnetClient.hpp" //- #include "TelnetClient.h"

//-only-file header
//-var {PRE} "MidiClient::"
class MidiClient : public MidiClientItf
{
public:
    //- {function} 0 1
    explicit MidiClient()
    //-only-file body
    {
        telnetClient.on_disconnect = [&]()
        {
            std::cerr << "[MAIN] Telnet disconnected, restart requested...\n";

            telnetDisconnected = true;
        };
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
    void getInPorts() override
    //-only-file body
    {
        std::cout << "\ninputs:\n";

        for (const libremidi::input_port &port : obs.get_input_ports())
        {
            std::cout << port.display_name << "\n";
        }
    }

    //- {fn}
    void getOutPorts() override
    //-only-file body
    {
        std::cout << "\noutputs:\n";
        for (const libremidi::output_port &port : obs.get_output_ports())
        {
            std::cout << port.display_name << "\n";
        }
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
    void testMidi() override
    //-only-file body
    {
        telnetDisconnected = false;
        std::string telnetHost = "localhost";
        std::string telnetPort = "5500";
        telnetClient.stop();
        if (!telnetClient.openSocket(telnetHost, telnetPort))
        {
            std::cout << "Telnet server - could not connect!" << std::endl;
            return;
        }

        std::string midiPortName = "Launch Control XL";
        int midiPortIdx = 0;

        auto port = getInPortByName(midiPortName);
        if (port)
        {
            std::cout << "Found port: " << port->display_name << std::endl;
        }
        else
        {
            std::cout << "Port not found!" << std::endl;
            return;
        }

        // Remove previous callback if exited
        std::erase_if(libreMidiInPorts, [&midiPortName, &midiPortIdx](const LibreMidiInPort &p)
                      { return p.getPortName() == midiPortName && p.getPortIdx() == midiPortIdx; });

        auto my_callback = [this](const libremidi::message &message)
        {
            // std::cerr << message.bytes.size() << "\n";
            // std::cerr << message.timestamp << "\n";

            if (message.get_message_type() == libremidi::message_type::NOTE_ON)
            {
                // std::cerr << "Notes ON\n";
            }
            else if (message.get_message_type() == libremidi::message_type::NOTE_OFF)
            {
                // std::cerr << "Notes OFF\n";
            }
            else if (message.get_message_type() == libremidi::message_type::CONTROL_CHANGE)
            {
                if (message.bytes[1] == 77)
                {
                    // std::cerr << "Control change throttle ";
                    double val = this->translateClamped(message.bytes[2], 0, 127, 0, 1);
                    // std::cerr << this->formatN(val,3) << "\n";
                    telnetClient.setValue("/controls/engines/engine[0]/throttle", this->formatN(val, 3));
                }
                else if (message.bytes[1] == 78)
                {
                    // std::cerr << "Control change rudder ";
                    double val = this->translateClamped(message.bytes[2], 0, 127, 1, -1);
                    // std::cerr << this->formatN(val,3) << "\n";
                    telnetClient.setValue("/controls/flight/rudder", this->formatN(val, 3));
                }
                else if (message.bytes[1] == 79)
                {
                    // std::cerr << "Control change aileron ";
                    double val = this->translateClamped(message.bytes[2], 0, 127, 1, -1);
                    // std::cerr << this->formatN(val,3) << "\n";
                    telnetClient.setValue("/controls/flight/aileron", this->formatN(val, 3));
                }
                else if (message.bytes[1] == 80)
                {
                    // std::cerr << "Control change elevator ";
                    double val = this->translateClamped(message.bytes[2], 0, 127, -1, 1);
                    // std::cerr << this->formatN(val,3) << "\n";
                    telnetClient.setValue("/controls/flight/elevator", this->formatN(val, 3));
                }
                else
                {
                    // std::cerr << "Control change\n";
                }
            }
        };

        libremidi::midi_in midi{
            libremidi::input_configuration{.on_message = my_callback}};

        LibreMidiInPort lmip{std::move(midiPortName), 0, std::move(midi), std::move(port.value())};
        lmip.open();
        libreMidiInPorts.push_back(std::move(lmip));
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

    //-only-file header
};
