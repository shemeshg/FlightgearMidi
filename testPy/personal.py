import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(script_dir, "..", "build", "FlightgearMidi")

#sys.path.append("../build/FlightgearMidi")
sys.path.append(module_dir)

import FlightgearMidi
import mido


novation_color_off = 12
novation_color_red = 15
novation_color_yellow = 62
novation_color_green = 60
hw_midi_outport = mido.open_output("Launch Control XL")
novation_flaps_led_id = 13
msg = mido.Message('note_on', note=novation_flaps_led_id, velocity=novation_color_off, channel=0)

def flaps_on_callback(key, val):
    try:
        val = float(val)
    except (ValueError, TypeError):
        return
                
    if val > 0.9:
        msg = mido.Message('note_on', note=novation_flaps_led_id, velocity=novation_color_red, channel=0)
        hw_midi_outport.send(msg)
    elif val >= 0.6:
        msg = mido.Message('note_on', note=novation_flaps_led_id, velocity=novation_color_yellow, channel=0)
        hw_midi_outport.send(msg)
    elif val >= 0.1:
        msg = mido.Message('note_on', note=novation_flaps_led_id, velocity=novation_color_green, channel=0)
        hw_midi_outport.send(msg)
    else:
        msg = mido.Message('note_on', note=novation_flaps_led_id, velocity=novation_color_off, channel=0)
        hw_midi_outport.send(msg)

def loadConfigData():
    cfg = FlightgearMidi.DataConfig()
    cfg.telnetHost = "localhost"
    #cfg.telnetHost = "ubuntumachine.local"
    cfg.telnetPort = "5500"

    # --- MIDI INPUT CONFIG ---
    midi_input = FlightgearMidi.DataConfigMidiInput()
    midi_input.midiInputIdx = 0
    midi_input.midiInputName = "Flightgear"
    # Helper to reduce repetition
    def add_mapping(fromStart, fromEnd, toStart, toEnd,
                    msgType, channel, cc, cmd):
        m = FlightgearMidi.DataConfigFromMidiToTelnet()
        m.fromStart = fromStart
        m.fromEnd = fromEnd
        m.toStart = toStart
        m.toEnd = toEnd
        m.midiMsgType = msgType
        m.midiChannel = channel
        m.notePitchOrCcChannel = cc
        m.setCmd = cmd
        midi_input.dataConfigFromMidiToTelnets.append(m)

    # Throttle
    add_mapping(
        0, 127, 0, 1,
        FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 77,
        "/controls/engines/engine[0]/throttle"
    )

    # Rudder
    add_mapping(
        0, 127, 1, -1,
        FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 78,
        "/controls/flight/rudder"
    )

    # Aileron
    add_mapping(
        0, 127, 1, -1,
        FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 79,
        "/controls/flight/aileron"
    )

    # Elevator
    add_mapping(
        0, 127, -1, 1,
        FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 80,
        "/controls/flight/elevator"
    )

    # Mixture
    add_mapping(
        0, 127, 0, 1,
        FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 84,
        "/controls/engines/current-engine/mixture"
    )

    cfg.dataConfigMidiInputs.append(midi_input)

    # --- FG PULLER KEYS ---
    #pull_throttle = FlightgearMidi.DataConfigPullerFgKey()
    #pull_throttle.fgKetPath = "/controls/engines/engine[0]/throttle"
    #pull_throttle.callback = lambda key, val: print(f"my key {key} val {val}")
    #cfg.dataConfigPullerFgKeys.append(pull_throttle)

    #pull_rudder = FlightgearMidi.DataConfigPullerFgKey()
    #pull_rudder.fgKetPath = "/controls/flight/rudder"
    #cfg.dataConfigPullerFgKeys.append(pull_rudder)

    pull_flaps = FlightgearMidi.DataConfigPullerFgKey()
    pull_flaps.fgKetPath = "/controls/flight/flaps"
    pull_flaps.callback = flaps_on_callback
    cfg.dataConfigPullerFgKeys.append(pull_flaps)
    

    return cfg



midi = FlightgearMidi.getMidiClientItf()
cfg = loadConfigData()
midi.setDataConfig(cfg)
cfg2 = midi.getDataConfig()


print("in ports:\n" + "\n".join(" " + p for p in midi.getInPorts()))
print("out ports:\n" + "\n".join(" " + p for p in midi.getOutPorts()))
print()

terminal_mode = False

try:
    if (not midi.startMidiClient()):
        exit(1)

    while True:
        if midi.getIsTelnetRunning():
            user_input = input()

            if terminal_mode:
                # In terminal mode, only raw commands are sent
                pass
            else:
                print("\nConnected\nq=quit\nt=terminal mode on/off")

            if user_input == "q":
                break

            elif user_input == "t":
                terminal_mode = not terminal_mode
                midi.setIsTerminalDebugMode(terminal_mode)

                if terminal_mode:
                    print("t - to exit terminal mode")

            elif terminal_mode:
                midi.sendTerminalRaw(user_input)

        else:
            # Not connected
            if midi.getIsTelnetDisconnectedSignal():
                print("Try to Restart")
                midi.startMidiClient()
            else:
                print("Not Connected\n r=restart q=quit")
                user_input = input()

                if user_input == "q":
                    break
                elif user_input == "r":
                    midi.startMidiClient()

except Exception as e:
    print(e)


