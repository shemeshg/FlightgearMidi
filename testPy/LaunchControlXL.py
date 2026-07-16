from dataclasses import dataclass
from typing import Any, Optional, Callable, List, Tuple
import sys

from FlightgearMidiHelper import (
    main_loop,
    FlightgearMidi,
    logger,
)

from FlightgearMidiUtils import (
    add_mappings,
    add_callback_mappings,
    add_pullers,
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
    state.midi_out.sendNoteOn(0, btn_id, COLOR["high"] if carb_on else COLOR["low"])


def on_off_toggle_callback(key: str, val: Any) -> None:
    state.carb_heat_on = not state.carb_heat_on
    cmd = "true" if state.carb_heat_on else "false"
    state.midi.sendTerminalRaw(f"set {key} {cmd}")


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
# CALLBACK FACTORIES
# ---------------------------------------------------------------------------

def make_toggle_callback(property_path: str) -> Callable:
    def _cb(val):
        on_off_toggle_callback(property_path, val)
    return _cb

def make_puller_callback(led_id: int) -> Callable:
    def _cb(key, val):
        pull_on_off_callback(led_id, key, val)
    return _cb

# ---------------------------------------------------------------------------
# CONFIG BUILDERS
# ---------------------------------------------------------------------------

def build_callback_mappings(toggle_mappings):
    result = []
    for midiMsgType, led_id, property_path in toggle_mappings:
        cb = make_toggle_callback(property_path)
        result.append((midiMsgType, led_id, cb))
    return result

def build_pullers(puller_mappings):
    result = []
    for property_path, led_id in puller_mappings:
        cb = make_puller_callback(led_id)
        result.append((property_path, cb))
    return result

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

    # Toggle mappings (MIDI → FG)
    toggle_mappings = [
        (FlightgearMidi.MidiMsgType.NOTE_ON, CARB_HEAT_LED_ID,
         "/controls/engines/current-engine/carb-heat")
    ]

    callback_mappings = build_callback_mappings(toggle_mappings)
    add_callback_mappings(midi_input, callback_mappings)

    cfg.dataConfigMidiInputs.append(midi_input)

    # Puller mappings (FG → LED)
    puller_mappings = [
        ("/controls/flight/flaps", FLAPS_LED_ID),
        ("/instrumentation/airspeed-indicator/indicated-speed-kt", AIR_SPEED_LED_ID),
    ]

    # Auto‑append pullers for every toggle mapping
    for _, led_id, property_path in toggle_mappings:
        puller_mappings.append((property_path, led_id))

    pullers = build_pullers(puller_mappings)
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
