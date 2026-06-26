//-define-file body hpp/MidiClient.cpp
//-define-file header hpp/MidiClient.h
//-only-file body //-
//- #include "MidiClient.h"
#include <iostream>
#include <algorithm>
#include <cmath>
#include <string>

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
  connect_on_start: true
  reconnect: true
  reconnect_delay: 2000   # ms
  read_interval: 50       # how often to poll telnet (ms)
  command_prefix: ""
  command_suffix: "\n"
  debug: false

  # When FlightGear sends property updates (because "follow" is enabled)
  # you can map them to MIDI outputs here:
  inbound:
    - id: mixture_feedback
      property: "/controls/engines/engine[0]/mixture"
      transform:
        from: [0, 1]
        to: [0, 127]
        round: 0
      midi_out:
        port: "Launch Control XL"
        type: control_change
        control: 77

presets:
  selected_1:
    active: true

midi:
  ports:
    - name: "Launch Control XL"
      index: 0
      mappings:
        - id: throttle
          presets:
            - selected_1
          match:
            type: control_change
            control: 77
          transform:
            from: [0, 127]
            to: [0, 1]
            round: 3
          command: "set /controls/engines/engine/throttle ${throttle}"
       - id: engine_start_macro
          match:
            type: note_on
            note: 40
          macro:
            - command: "/controls/engines/engine[0]/starter 1"
            - command: "/controls/engines/engine[0]/mixture 1"
            - command: "/controls/engines/engine[0]/throttle 0.2"
            - delay: 500   # milliseconds
            - command: "/controls/engines/engine[0]/starter 0"
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
        std::erase_if(libreMidiInPorts, [&portName, &portIdx](const LibreMidiInPort &p)
                      { return p.getPortName() == portName && p.getPortIdx() == portIdx; });

        auto my_callback = [this](const libremidi::message &message)
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
                if (message.bytes[1] == 77)
                {
                    std::cerr << "Control change throttle ";
                    double val = this->translateClamped(message.bytes[2], 0, 127, 0, 1);
                    std::cerr << this->formatN(val,3) << "\n";
                }
                else
                {
                    std::cerr << "Control change\n";
                }
            }
        };

        libremidi::midi_in midi{
            libremidi::input_configuration{.on_message = my_callback}};

        LibreMidiInPort lmip{std::move(portName), 0, std::move(midi), std::move(port.value())};
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
    libremidi::observer obs;

    std::vector<LibreMidiInPort> libreMidiInPorts;

    //-only-file header
};
