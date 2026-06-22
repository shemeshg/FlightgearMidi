//-define-file body hpp/MidiClient.cpp
//-define-file header hpp/MidiClient.h
//-only-file body //-
//- #include "MidiClient.h"
#include <iostream>
#include <libremidi/libremidi.hpp>

//-only-file header //-
#pragma once
//- {include-header}
#include "MidiClientItf.hpp" //- #include "MidiClientItf.h"
//- {include-body}
#include "midievent.hpp" //- #include "midievent.h"


//-only-file header
//-var {PRE} "MidiClient::"
class MidiClient: public MidiClientItf {
public:

//- {fn}
void testMidi() override
//-only-file body
{
    std::cout << "\ninputs:\n";
    libremidi::observer obs;
    for (const libremidi::input_port &port : obs.get_input_ports())
    {
        std::cout << port.display_name << "\n";
    }
    std::cout << "\noutputs:\n";
    for (const libremidi::output_port &port : obs.get_output_ports())
    {
        std::cout << port.display_name << "\n";
    }
    auto my_callback = [](const libremidi::message& message) {
      // how many bytes
      //message.size();
      // access to the individual bytes
      //message[i];
      // access to the timestamp
      std::cerr<< message.bytes.size()<<"\n";
      std::cerr<< message.timestamp<<"\n";
      int portIdx=1;
      std::string portName = "asdf";
      MidiEvent me{message.timestamp, message.bytes, portIdx,portName};
      std::cerr<< me.commandStr()<<"\n";
      //libremidi::message_type::NOTE_ON
      std::cerr<<"msg type "<<(int)message.get_message_type();
      //libremidi::channel_events::note_on
    };

   libremidi::midi_in midi { 
      libremidi::input_configuration{ .on_message = my_callback } 
    };
    midi.open_port(obs.get_input_ports()[1]);
    std::string userInput;
    std::getline(std::cin, userInput);
}

//-only-file header
private:

};
