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
        std::string portName = "Launch Control XL";
        int portIdx = 0;
        /*
telnet:
  host: "localhost"
  port: 5500

midi:
  ports:
    - name: "Launch Control XL"
      index: 0
      mappings:
        - id: throttle
          match:
            type: control_change
            control: 77
          transform:
            from: [0, 127]
            to: [0, 1]
            round: 3
          command: "/controls/engines/engine/throttle ${throttle}"
        */


        auto port = getInPortByName(portName);
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
        std::erase_if(libreMidiInPorts, [&portName, &portIdx](const LibreMidiInPort& p) {
            return p.getPortName() == portName && p.getPortIdx() == portIdx;
        }) ;



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
