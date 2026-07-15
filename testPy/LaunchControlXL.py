from dataclasses import dataclass
from typing import Any, Optional, Callable, List, Tuple
import sys

from FlightgearMidiHelper import (
    main_loop,
    add_mappings,
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
}

FLAPS_LED_ID = 13 + 16 * 0
AIR_SPEED_LED_ID = 73
CARB_HEAT_LED_ID = 105

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


def pull_carb_heat_callback(key: str, val: str) -> None:
    v = val.strip().lower()
    if v not in ("true", "false"):
        return

    carb_on = (v == "true")
    state.midi_out.sendNoteOn(0, CARB_HEAT_LED_ID, 127 if carb_on else 0)


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
    carb_heat = FlightgearMidi.DataConfigFromMidiToTelnet()
    carb_heat.midiMsgType = FlightgearMidi.MidiMsgType.NOTE_ON
    carb_heat.notePitchOrCcChannel = CARB_HEAT_LED_ID
    carb_heat.isCallback = True
    carb_heat.callback = carb_heat_toggle_callback
    midi_input.dataConfigFromMidiToTelnets.append(carb_heat)

    cfg.dataConfigMidiInputs.append(midi_input)

    # Pullers (FG → callbacks)
    pullers: List[Tuple[str, Callable]] = [
        ("/controls/flight/flaps", flaps_on_callback),
        ("/instrumentation/airspeed-indicator/indicated-speed-kt",
         pull_indicated_air_speed_callback),
        ("/controls/engines/current-engine/carb-heat",
         pull_carb_heat_callback),
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
