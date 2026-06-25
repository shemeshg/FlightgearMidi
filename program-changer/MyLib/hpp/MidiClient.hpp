//-define-file body hpp/MidiClient.cpp
//-define-file header hpp/MidiClient.h
//-only-file body //-
//- #include "MidiClient.h"
#include <iostream>

//-only-file header //-
#pragma once
#include <libremidi/libremidi.hpp>
#include <optional>

//- {include-header}
#include "MidiClientItf.hpp" //- #include "MidiClientItf.h"
//- {include-header}
#include "LibreMidiInPort.hpp" //- #include "LibreMidiInPort.h"

//-only-file header
//-var {PRE} "MidiClient::"
class MidiClient : public MidiClientItf
{
public:
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
        //assume it  is not yet in cash
        std::string portName = "Launch Control XL";
        auto port = getInPortByName(portName);
        if (port)
        {
            // Port exists, safe to use
            std::cout << "Found port: " << port->display_name << std::endl;
        }
        else
        {
            // Port was not found (returned std::nullopt)
            std::cout << "Port not found!" << std::endl;
            return;
        }

       


        auto my_callback = [](const libremidi::message &message)
        {
            std::cerr << message.bytes.size() << "\n";
            std::cerr << message.timestamp << "\n";

            if (message.get_message_type() == libremidi::message_type::NOTE_ON)
            {
                std::cerr << "Notes ON\n";
            }
            else if (message.get_message_type() == libremidi::message_type::NOTE_OFF)
            {
                std::cerr << "Notes OFF\n";
            }
            else if (message.get_message_type() == libremidi::message_type::CONTROL_CHANGE)
            {
                std::cerr << "Control change\n";
            }
        };

        libremidi::midi_in midi{
            libremidi::input_configuration{.on_message = my_callback}};

        LibreMidiInPort lmip{std::move(portName), 0,std::move(midi), std::move(port.value())};
        lmip.open();
        libreMidiInPorts.push_back(std::move(lmip));
    }

    //-only-file header
private:
    libremidi::observer obs;


    std::vector<LibreMidiInPort> libreMidiInPorts;
};
