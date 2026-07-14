import os
import sys
import logging
from dataclasses import dataclass
from typing import Optional, Any

# ---------------------------------------------------------------------------
# MODULE PATH SETUP
# ---------------------------------------------------------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(script_dir, "..", "build", "FlightgearMidi")
sys.path.append(module_dir)

import FlightgearMidi
print("Loaded module from:", FlightgearMidi.__file__)

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

MIDI_INPUT_NAME = "FlightgearOut"
MIDI_INPUT_INDEX = 0

MIDI_OUTPUT_NAME = "FlightgearIn"
MIDI_OUTPUT_INDEX = 0

TELNET_HOST = "localhost"
TELNET_PORT = "5500"

# Novation LED colors
COLOR = {
    "off": 12,
    "red_dim": 13,
    "red": 15,
    "red_blink": 11,
    "yellow": 62,
    "yellow_blink": 58,
    "green_dim": 28,
    "green": 60,
    "green_blink": 56,
    "amber_dim": 29,
    "amber": 63,
    "amber_blink": 59,
}

FLAPS_LED_ID = 13 + 16 * 0
AIR_SPEED_LED_ID = 73

# ---------------------------------------------------------------------------
# APP STATE
# ---------------------------------------------------------------------------

@dataclass
class AppState:
    midi: Optional[Any] = None
    midi_out: Optional[Any] = None
    previous_air_speed: Optional[int] = None
    carb_heat_on: bool = False


state = AppState()

# ---------------------------------------------------------------------------
# CALLBACKS
# ---------------------------------------------------------------------------

def pull_indicated_air_speed_callback(key: str, val: Any) -> None:
    try:
        speed = float(val)
    except Exception:
        return

    if speed > 70:
        color = COLOR["off"]
    elif speed >= 50:
        color = COLOR["green"]
    elif speed >= 40:
        color = COLOR["yellow"]
    else:
        color = COLOR["red"]

    if color != state.previous_air_speed:
        state.previous_air_speed = color
        state.midi_out.sendNoteOn(0, AIR_SPEED_LED_ID, color)


def pull_carb_heat_callback(key: str, val: str) -> None:
    v = val.strip().lower()

    if v == "true":
        carb = 1
    elif v == "false":
        carb = 0
    else:
        try:
            carb = float(v)
        except Exception:
            return

    state.midi_out.sendNoteOn(0, 105, 127 if carb == 1 else 0)


def carb_heat_toggle_callback(val: Any) -> None:
    state.carb_heat_on = not state.carb_heat_on
    cmd = "true" if state.carb_heat_on else "false"
    state.midi.sendTerminalRaw(f"set /controls/engines/current-engine/carb-heat {cmd}")


def flaps_on_callback(key: str, val: Any) -> None:
    try:
        flap = float(val)
    except Exception:
        return

    if flap > 0.9:
        color = COLOR["red"]
    elif flap >= 0.6:
        color = COLOR["yellow"]
    elif flap >= 0.1:
        color = COLOR["green"]
    else:
        color = COLOR["off"]

    state.midi_out.sendNoteOn(0, FLAPS_LED_ID, color)

# ---------------------------------------------------------------------------
# CONFIG CREATION
# ---------------------------------------------------------------------------

def add_mapping(midi_input, from_start, from_end, to_start, to_end, msg_type, channel, cc, cmd):
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


def loadConfigData() -> FlightgearMidi.DataConfig:
    cfg = FlightgearMidi.DataConfig()
    cfg.telnetHost = TELNET_HOST
    cfg.telnetPort = TELNET_PORT

    midi_input = FlightgearMidi.DataConfigMidiInput()
    midi_input.midiInputIdx = MIDI_INPUT_INDEX
    midi_input.midiInputName = MIDI_INPUT_NAME

    # Control mappings
    mappings = [
        (0, 127, 0, 1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 77,
         "/controls/engines/engine[0]/throttle"),
        (0, 127, 1, -1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 78,
         "/controls/flight/rudder"),
        (0, 127, 1, -1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 79,
         "/controls/flight/aileron"),
        (0, 127, -1, 1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 80,
         "/controls/flight/elevator"),
        (0, 127, 0, 1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 84,
         "/controls/engines/current-engine/mixture"),
    ]

    for args in mappings:
        add_mapping(midi_input, *args)

    # Carb heat toggle
    carb_heat = FlightgearMidi.DataConfigFromMidiToTelnet()
    carb_heat.midiMsgType = FlightgearMidi.MidiMsgType.NOTE_ON
    carb_heat.notePitchOrCcChannel = 105
    carb_heat.isCallback = True
    carb_heat.callback = carb_heat_toggle_callback
    midi_input.dataConfigFromMidiToTelnets.append(carb_heat)

    cfg.dataConfigMidiInputs.append(midi_input)

    # Puller keys
    def add_puller(path, cb):
        p = FlightgearMidi.DataConfigPullerFgKey()
        p.fgKetPath = path
        p.callback = cb
        cfg.dataConfigPullerFgKeys.append(p)

    add_puller("/controls/flight/flaps", flaps_on_callback)
    add_puller("/instrumentation/airspeed-indicator/indicated-speed-kt",
               pull_indicated_air_speed_callback)
    add_puller("/controls/engines/current-engine/carb-heat",
               pull_carb_heat_callback)

    return cfg

# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

def main():
    state.midi = FlightgearMidi.getMidiClientItf()
    state.midi.pullerSleepInterval = 200

    cfg = loadConfigData()
    state.midi.setDataConfig(cfg)

    logger.info("Available MIDI input ports:\n%s",
                "\n".join(" " + p for p in state.midi.getInPorts()))
    logger.info("Available MIDI output ports:\n%s",
                "\n".join(" " + p for p in state.midi.getOutPorts()))

    if not state.midi.openLibreMidiOutPort(MIDI_OUTPUT_NAME, MIDI_OUTPUT_INDEX):
        logger.error("Failed to open MIDI output port.")
        sys.exit(1)

    state.midi_out = state.midi.getLibreMidiOutPort(MIDI_OUTPUT_NAME, MIDI_OUTPUT_INDEX)

    # Initialize LEDs
    state.midi_out.sendNoteOn(0, FLAPS_LED_ID, COLOR["off"])
    state.midi_out.sendNoteOn(0, AIR_SPEED_LED_ID, COLOR["off"])

    terminal_mode = False

    try:
        if not state.midi.startMidiClient():
            logger.error("Failed to start MIDI client.")
            sys.exit(1)

        while True:
            if state.midi.getIsTelnetRunning():
                user_input = input()

                if not terminal_mode:
                    logger.info("Connected\nq=quit\nt=toggle terminal mode")

                if user_input == "q":
                    break
                elif user_input == "t":
                    terminal_mode = not terminal_mode
                    state.midi.setIsTerminalDebugMode(terminal_mode)
                    if terminal_mode:
                        logger.info("Terminal mode enabled.")
                elif terminal_mode:
                    state.midi.sendTerminalRaw(user_input)

            else:
                if state.midi.getIsTelnetDisconnectedSignal():
                    logger.warning("Disconnected. Attempting restart...")
                    state.midi.startMidiClient()
                else:
                    logger.info("Not Connected\n r=restart q=quit")
                    user_input = input()

                    if user_input == "q":
                        break
                    elif user_input == "r":
                        state.midi.startMidiClient()

    except Exception as e:
        logger.exception("Unhandled exception: %s", e)


if __name__ == "__main__":
    main()
