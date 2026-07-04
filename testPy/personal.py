import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(script_dir, "..", "build", "FlightgearMidi")

#sys.path.append("../build/FlightgearMidi")
sys.path.append(module_dir)

import FlightgearMidi
import mido
#print(mido.get_output_names())
#exit(0)

novation_color_off = 12

novation_color_red_dim = 13
novation_color_red = 15
novation_color_red_blink = 11

novation_color_yellow = 62
novation_color_yellow_blink = 58

novation_color_green_dim = 28
novation_color_green = 60
novation_color_green_blink = 56

novation_color_amber_dim = 29
novation_color_amber = 63
novation_color_amber_blink = 59


# midio bug can list virtual ports but not send to
hw_midi_outport = mido.open_output("Launch Control XL")
# rottery leds are 13 + row_offset + 16 * column_offset
# btn leds are 41..44 57..60
# btn leds are 73..76 89..92

novation_flaps_led_id = 13 + 0 + 16 * 0
novation_air_speed_id = 73
msg = mido.Message('note_on', note=novation_flaps_led_id, velocity=novation_color_off, channel=0)
hw_midi_outport.send(msg)
msg = mido.Message('note_on', note=novation_air_speed_id, velocity=novation_color_off, channel=0)
hw_midi_outport.send(msg)

previous_air_speed_state = None
def pull_indicated_air_speed_callback(key, val):    
    try:
        val = float(val)
    except (ValueError, TypeError):
        return
    global previous_air_speed_state 

    current_air_speed_state = novation_color_off
    if val > 70:
        current_air_speed_state = novation_color_off
    elif val >= 50:
        current_air_speed_state = novation_color_green
    elif val >= 40:
        current_air_speed_state = novation_color_yellow    
    else:
        current_air_speed_state = novation_color_red
        
    if current_air_speed_state != previous_air_speed_state:
        previous_air_speed_state = current_air_speed_state
        msg = mido.Message('note_on', note=novation_air_speed_id, velocity=current_air_speed_state, channel=0)
        hw_midi_outport.send(msg)






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
    
    pull_indicated_air_speed = FlightgearMidi.DataConfigPullerFgKey()
    pull_indicated_air_speed.fgKetPath = "/instrumentation/airspeed-indicator/indicated-speed-kt"
    pull_indicated_air_speed.callback = pull_indicated_air_speed_callback
    cfg.dataConfigPullerFgKeys.append(pull_indicated_air_speed)    

    return cfg



midi = FlightgearMidi.getMidiClientItf()
midi.pullerSleepInterval = 200
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


