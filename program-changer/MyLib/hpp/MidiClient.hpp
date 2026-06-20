//-define-file body hpp/MidiClient.cpp
//-define-file header hpp/MidiClient.h
//-only-file body //-
//- #include "MidiClient.h"
#include <iostream>
#include <libremidi/libremidi.hpp>

//-only-file header //-
#pragma once

//-only-file header
//-var {PRE} ""

//- {fn}
void printShalom()
//-only-file body
{
    std::cout << "\ninputs:\n";
    libremidi::observer obs;
    for (const libremidi::input_port &port : obs.get_input_ports())
    {
        std::cout << port.port_name << "\n";
    }
    std::cout << "\noutputs:\n";
    for (const libremidi::output_port &port : obs.get_output_ports())
    {
        std::cout << port.port_name << "\n";
    }
}
