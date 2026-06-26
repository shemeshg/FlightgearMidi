//-define-file body hpp/MidiClientUtil.cpp
//-define-file header hpp/MidiClientUtil.h
//-only-file body //-
//- #include "MidiClientUtil.h"
//-only-file header //-
#pragma once
//- {include-header}
#include "MidiClientItf.hpp" //- #include "MidiClientItf.h"


//- {include-body}
#include "MidiClient.hpp" //- #include "MidiClient.h"

//-var {PRE} ""
//- {fn}
std::unique_ptr<MidiClientItf>  getMidiClientItf()
//-only-file body
{
    return std::make_unique<MidiClient>();
}