//-define-file body hpp/MidiClient.cpp
//-define-file header hpp/MidiClient.h
//-only-file body //-
//- #include "MidiClient.h"
#include <iostream>
#include <ranges>

//-only-file header //-
#pragma once
#include <libremidi/libremidi.hpp>

//- {include-header}
#include "MidiClientItf.hpp" //- #include "MidiClientItf.h"

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


    

    //- {function} 0 2
    const libremidi::input_port *getInPortByName(std::string portName, int idx = 0) 
    //-only-file body
    {        
        int foundItems = 0;

        for (const libremidi::input_port &port : obs.get_input_ports())
        {
            if (port.display_name == portName) {
                if (idx == foundItems) {
                    return &port;

                }
                foundItems++;
            } 
        }        
         return nullptr;
    }

    //- {fn}
    void testMidi() override
    //-only-file body
    {
        std::cout << "\ninputs:\n";

        for (const libremidi::input_port &port : obs.get_input_ports())
        {
            std::cout << port.display_name << "\n";
        }
        std::cout << "\noutputs:\n";
        for (const libremidi::output_port &port : obs.get_output_ports())
        {
            std::cout << port.display_name << "\n";
        }
        auto my_callback = [](const libremidi::message &message)
        {
            // how many bytes
            // message.size();
            // access to the individual bytes
            // message[i];
            // access to the timestamp
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
        midi.open_port(obs.get_input_ports()[1]);
        std::string userInput;
        std::getline(std::cin, userInput);
    }

    //-only-file header
private:
    libremidi::observer obs;
    struct LibreMidiPort
    {
        std::string portName;
    };
};
