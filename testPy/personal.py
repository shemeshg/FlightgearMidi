import os
import sys
import logging
from typing import Optional, Callable, Any

# ---------------------------------------------------------------------------
# GLOBAL CONSTANTS (easy to notice)
# ---------------------------------------------------------------------------

MIDI_INPUT_NAME: str = "FlightgearOut"
MIDI_INPUT_INDEX: int = 0

MIDI_OUTPUT_NAME: str = "FlightgearIn"
MIDI_OUTPUT_INDEX: int = 0

TELNET_HOST: str = "localhost"
TELNET_PORT: str = "5500"

# ---------------------------------------------------------------------------
# MODULE PATH SETUP
# ---------------------------------------------------------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(script_dir, "..", "build", "FlightgearMidi")
sys.path.append(module_dir)

import FlightgearMidi  # noqa: E402


# ---------------------------------------------------------------------------
# LOGGING SETUP
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# NOVATION LED COLORS
# ---------------------------------------------------------------------------

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

# LED IDs
novation_flaps_led_id = 13 + 16 * 0
novation_air_speed_id = 73

# ---------------------------------------------------------------------------
# GLOBAL MIDI STATE
# ---------------------------------------------------------------------------

midiOutPort: Optional[Any] = None
previous_air_speed_state: Optional[int] = None


# ---------------------------------------------------------------------------
# CALLBACKS
# ---------------------------------------------------------------------------

def pull_indicated_air_speed_callback(key: str, val: Any) -> None:
    """Update airspeed LED based on indicated airspeed."""
    global previous_air_speed_state, midiOutPort

    try:
        speed = float(val)
    except (ValueError, TypeError):
        return

    if speed > 70:
        current_state = novation_color_off
    elif speed >= 50:
        current_state = novation_color_green
    elif speed >= 40:
        current_state = novation_color_yellow
    else:
        current_state = novation_color_red

    if current_state != previous_air_speed_state:
        previous_air_speed_state = current_state
        midiOutPort.sendNoteOn(0, novation_air_speed_id, current_state)


def pull_carb_heat_callback(key: str, val: str) -> None:
    global midiOutPort

    v = val.strip().lower()

    # Boolean strings
    if v == "true":
        carb_heat = 1.0
    elif v == "false":
        carb_heat = 0.0
    else:
        # Numeric strings
        try:
            carb_heat = float(v)
        except ValueError:
            print(f"Invalid carb_heat value: {val}")
            return
        
    if carb_heat == 1:  
        midiOutPort.sendNoteOn(0, 105, 127)
    elif carb_heat == 0:
        midiOutPort.sendNoteOn(0, 105, 0)
    else:
        return

    



def flaps_on_callback(key: str, val: Any) -> None:
    """Update flaps LED based on flap position."""
    global midiOutPort

    try:
        flap_val = float(val)
    except (ValueError, TypeError):
        return

    if flap_val > 0.9:
        color = novation_color_red
    elif flap_val >= 0.6:
        color = novation_color_yellow
    elif flap_val >= 0.1:
        color = novation_color_green
    else:
        color = novation_color_off

    midiOutPort.sendNoteOn(0, novation_flaps_led_id, color)


# ---------------------------------------------------------------------------
# CONFIG LOADER
# ---------------------------------------------------------------------------

def loadConfigData() -> FlightgearMidi.DataConfig:
    cfg = FlightgearMidi.DataConfig()
    cfg.telnetHost = TELNET_HOST
    cfg.telnetPort = TELNET_PORT

    midi_input = FlightgearMidi.DataConfigMidiInput()
    midi_input.midiInputIdx = MIDI_INPUT_INDEX
    midi_input.midiInputName = MIDI_INPUT_NAME

    def add_mapping(
        from_start: int,
        from_end: int,
        to_start: int,
        to_end: int,
        msg_type: int,
        channel: int,
        cc: int,
        cmd: str
    ) -> None:
        m = FlightgearMidi.DataConfigFromMidiToTelnet()
        m.fromStart = from_start
        m.fromEnd = from_end
        m.toStart = to_start
        m.toEnd = to_end
        m.midiMsgType = msg_type
        m.midiChannel = channel
        m.notePitchOrCcChannel = cc
        m.setCmd = cmd
        midi_input.dataConfigFromMidiToTelnets.append(m)

    # Control mappings
    add_mapping(0, 127, 0, 1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 77,
                "/controls/engines/engine[0]/throttle")
    add_mapping(0, 127, 1, -1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 78,
                "/controls/flight/rudder")
    add_mapping(0, 127, 1, -1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 79,
                "/controls/flight/aileron")
    add_mapping(0, 127, -1, 1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 80,
                "/controls/flight/elevator")
    add_mapping(0, 127, 0, 1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 84,
                "/controls/engines/current-engine/mixture")

    cfg.dataConfigMidiInputs.append(midi_input)

    # Puller keys
    pull_flaps = FlightgearMidi.DataConfigPullerFgKey()
    pull_flaps.fgKetPath = "/controls/flight/flaps"
    pull_flaps.callback = flaps_on_callback
    cfg.dataConfigPullerFgKeys.append(pull_flaps)

    pull_ias = FlightgearMidi.DataConfigPullerFgKey()
    pull_ias.fgKetPath = "/instrumentation/airspeed-indicator/indicated-speed-kt"
    pull_ias.callback = pull_indicated_air_speed_callback
    cfg.dataConfigPullerFgKeys.append(pull_ias)


    pull_carb_heat = FlightgearMidi.DataConfigPullerFgKey()
    pull_carb_heat.fgKetPath = "/controls/engines/current-engine/carb-heat"
    pull_carb_heat.callback = pull_carb_heat_callback
    cfg.dataConfigPullerFgKeys.append(pull_carb_heat)
    


    return cfg


# ---------------------------------------------------------------------------
# MAIN APPLICATION LOOP
# ---------------------------------------------------------------------------

def main() -> None:
    global midiOutPort

    midi = FlightgearMidi.getMidiClientItf()
    midi.pullerSleepInterval = 200

    cfg = loadConfigData()
    midi.setDataConfig(cfg)

    logger.info("Available MIDI input ports:\n%s",
                "\n".join(" " + p for p in midi.getInPorts()))
    logger.info("Available MIDI output ports:\n%s",
                "\n".join(" " + p for p in midi.getOutPorts()))

    if not midi.openLibreMidiOutPort(MIDI_OUTPUT_NAME, MIDI_OUTPUT_INDEX):
        logger.error("Failed to open MIDI output port. "
                     "Ensure MidiRouterClient created the virtual port.")
        sys.exit(1)

    midiOutPort = midi.getLibreMidiOutPort(MIDI_OUTPUT_NAME, MIDI_OUTPUT_INDEX)

    midiOutPort.sendNoteOn(0, novation_flaps_led_id, novation_color_off)
    midiOutPort.sendNoteOn(0, novation_air_speed_id, novation_color_off)

    terminal_mode = False

    try:
        if not midi.startMidiClient():
            logger.error("Failed to start MIDI client.")
            sys.exit(1)

        while True:
            if midi.getIsTelnetRunning():
                user_input = input()

                if not terminal_mode:
                    logger.info("Connected\nq=quit\nt=toggle terminal mode")

                if user_input == "q":
                    break
                elif user_input == "t":
                    terminal_mode = not terminal_mode
                    midi.setIsTerminalDebugMode(terminal_mode)
                    if terminal_mode:
                        logger.info("Terminal mode enabled. Press 't' to exit.")
                elif terminal_mode:
                    midi.sendTerminalRaw(user_input)

            else:
                if midi.getIsTelnetDisconnectedSignal():
                    logger.warning("Disconnected. Attempting restart...")
                    midi.startMidiClient()
                else:
                    logger.info("Not Connected\n r=restart q=quit")
                    user_input = input()

                    if user_input == "q":
                        break
                    elif user_input == "r":
                        midi.startMidiClient()

    except Exception as e:
        logger.exception("Unhandled exception occurred: %s", e)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
