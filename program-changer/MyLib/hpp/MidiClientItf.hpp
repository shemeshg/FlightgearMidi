//-define-file body hpp/MidiClientItf.cpp
//-define-file header hpp/MidiClientItf.h
//-only-file body //-
//- #include "MidiClientItf.h"




//-only-file header //-
#pragma once
#include <memory>

//-only-file header
//-var {PRE} "MidiClientItf::"
class MidiClientItf {
public:    
    virtual void testMidi() = 0;
    virtual ~MidiClientItf() = default;
};


