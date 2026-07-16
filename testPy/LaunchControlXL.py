from dataclasses import dataclass
from typing import Any, Optional, Callable, List, Tuple
import sys

from FlightgearMidiHelper import (
    main_loop,
    add_mappings,
    add_callback_mappings,
    add_pullers,
    FlightgearMidi,
    logger,
)

# ---------------------------------------------------------------------------
# APP STATE
# ---------------------------------------------------------------------------

@dataclass
class AppState:
    midi: Optional[Any] = None
    midi_out: Optional[Any] = None
    previous_air_speed_color: Optional[int] = None
    carb_heat_on: bool = False


state = AppState()

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

MIDI_INPUT_NAME = "FlightgearOut"
MIDI_INPUT_INDEX = 0

MIDI_OUTPUT_NAME = "FlightgearIn"
MIDI_OUTPUT_INDEX = 0

TELNET_HOST = "localhost"
TELNET_PORT = "5500"

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
    "high": 127,
    "low": 0

}

FLAPS_LED_ID = 13 + 16 * 0
AIR_SPEED_LED_ID = 73

CARB_HEAT_LED_ID = 105
LANDING_LIGHTS_LED_ID = 106
TAXI_LIGHT_LED_ID = 107

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

    if color != state.previous_air_speed_color:
        state.previous_air_speed_color = color
        state.midi_out.sendNoteOn(0, AIR_SPEED_LED_ID, color)


def pull_on_off_callback(btn_id: int, key: str, val: str) -> None:
    v = val.strip().lower()
    if v not in ("true", "false"):
        return

    carb_on = (v == "true")
    state.midi_out.sendNoteOn(0, btn_id, COLOR["high"]  if carb_on else COLOR["low"] )




def on_off_toggle_callback(key:str , val: Any) -> None:
    state.carb_heat_on = not state.carb_heat_on
    cmd = "true" if state.carb_heat_on else "false"
    state.midi.sendTerminalRaw(
        f"set {key} {cmd}"
    )

def carb_heat_toggle_callback(val: Any) -> None:
    state.carb_heat_on = not state.carb_heat_on
    cmd = "true" if state.carb_heat_on else "false"
    state.midi.sendTerminalRaw(
        f"set /controls/engines/current-engine/carb-heat {cmd}"
    )


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
# CONFIG LOADING
# ---------------------------------------------------------------------------

def loadConfigData() -> FlightgearMidi.DataConfig:
    cfg = FlightgearMidi.DataConfig()
    cfg.telnetHost = TELNET_HOST
    cfg.telnetPort = TELNET_PORT

    # MIDI input configuration
    midi_input = FlightgearMidi.DataConfigMidiInput()
    midi_input.midiInputIdx = MIDI_INPUT_INDEX
    midi_input.midiInputName = MIDI_INPUT_NAME

    # CC → Telnet mappings
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

    add_mappings(midi_input, mappings)

    # Carb heat toggle (NOTE ON → callback)
    def make_toggle_callback(property_path):
        def _cb(val):
            on_off_toggle_callback(property_path, val)
        return _cb
    
    callback_mappings = [
        (
            FlightgearMidi.MidiMsgType.NOTE_ON, 
            CARB_HEAT_LED_ID, 
            make_toggle_callback("/controls/engines/current-engine/carb-heat")
         )        
    ]
    add_callback_mappings(midi_input, callback_mappings)


    cfg.dataConfigMidiInputs.append(midi_input)

    # Pullers (FG → callbacks)
    pullers: List[Tuple[str, Callable]] = [
        ("/controls/flight/flaps", flaps_on_callback),
        ("/instrumentation/airspeed-indicator/indicated-speed-kt",
         pull_indicated_air_speed_callback),
        ("/controls/engines/current-engine/carb-heat",
         lambda key,val: pull_on_off_callback(CARB_HEAT_LED_ID, key,val)
        ),
    ]

    add_pullers(cfg.dataConfigPullerFgKeys, pullers)

    return cfg

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    state.midi = FlightgearMidi.getMidiClientItf()
    state.midi.pullerSleepInterval = 200
    state.midi.setDataConfig(loadConfigData())

    logger.info("Available MIDI input ports:\n%s",
                "\n".join(" " + p for p in state.midi.getInPorts()))
    logger.info("Available MIDI output ports:\n%s",
                "\n".join(" " + p for p in state.midi.getOutPorts()))

    if not state.midi.openLibreMidiOutPort(MIDI_OUTPUT_NAME, MIDI_OUTPUT_INDEX):
        logger.error("Failed to open MIDI output port.")
        sys.exit(1)

    state.midi_out = state.midi.getLibreMidiOutPort(
        MIDI_OUTPUT_NAME, MIDI_OUTPUT_INDEX
    )

    # Initialize LEDs
    state.midi_out.sendNoteOn(0, FLAPS_LED_ID, COLOR["off"])
    state.midi_out.sendNoteOn(0, AIR_SPEED_LED_ID, COLOR["off"])

    main_loop(state.midi)
