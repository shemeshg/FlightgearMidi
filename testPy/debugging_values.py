# temporary script to debug FG values using telnet and httpd async
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(script_dir, "..", "build", "FlightgearMidi")

#sys.path.append("../build/FlightgearMidi")
sys.path.append(module_dir)

import FlightgearMidi

cfg = FlightgearMidi.DataConfig()
cfg.telnetHost = "localhost"
cfg.telnetPort = "5500"
cfg.httpdPort = "8800"
midi = FlightgearMidi.getMidiClientItf()
midi.setDataConfig(cfg)
midi.startMidiClient()
if midi.getIsTelnetRunning():    
    print(midi.debugTelnetGet("/orientation/heading-deg"))
    # async multiple requests
    print(midi.debugHttpGet({"/orientation/heading-deg": ""}))
    user_input = input()   
 

