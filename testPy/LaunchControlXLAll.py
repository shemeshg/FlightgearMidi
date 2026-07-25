from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
import sys

from FlightgearMidiUtils import apply_midi_bindings
from FlightgearMidiHelper import FlightgearMidi, logger

# ---------------------------------------------------------------------------
# DEVICE CLASS
# ---------------------------------------------------------------------------

@dataclass
class LaunchControlXLAll:
    midi: Optional[Any] = None
    midi_out: Optional[Any] = None

    previous_air_speed_color: Optional[int] = None
    toggle_states: Dict[str, bool] = field(default_factory=dict)

    # Instance-level lists (class-level mutables are dangerous)
    mappings: List[Any] = field(default_factory=list)
    toggle_mappings: List[Any] = field(default_factory=list)
    puller_mappings: List[Any] = field(default_factory=list)

    # -------------------------------------------------------
    # CONSTANTS
    # -------------------------------------------------------

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
        "low": 0,
    }

    FLAPS_LED_ID = 13 + 16 * 0
    AIR_SPEED_LED_ID = 73

    CARB_HEAT_LED_ID = 105
    LANDING_LIGHTS_LED_ID = 106
    TAXI_LIGHT_LED_ID = 107

    # -------------------------------------------------------
    # ABSTRACT METHOD
    # -------------------------------------------------------

    def set_mappings(self) -> None:
        """
        Override this in subclasses.
        """
        raise NotImplementedError("set_mappings() must be implemented in subclass")

    # -------------------------------------------------------
    # CALLBACKS
    # -------------------------------------------------------

    def pull_indicated_air_speed(self, key: str, val: str) -> None:
        try:
            speed = float(val)
        except ValueError:
            return

        if speed > 70:
            color = self.COLOR["off"]
        elif speed >= 50:
            color = self.COLOR["green"]
        elif speed >= 40:
            color = self.COLOR["yellow"]
        else:
            color = self.COLOR["red"]

        if color != self.previous_air_speed_color:
            self.previous_air_speed_color = color
            self.midi_out.sendNoteOn(0, self.AIR_SPEED_LED_ID, color)

    def pull_on_off(self, btn_id: int, key: str, val: str) -> None:
        v = val.strip().lower().replace('"', '')
        if v not in ("true", "false"):
            return

        is_on = (v == "true")
        self.midi_out.sendNoteOn(
            0, btn_id,
            self.COLOR["high"] if is_on else self.COLOR["low"]
        )

    def on_off_toggle(self, key: str, val: Any) -> None:
        new_state = not self.toggle_states.get(key, False)
        self.toggle_states[key] = new_state
        self.midi.sendTerminalRaw(f"set {key} {'true' if new_state else 'false'}")

    def flaps_on(self, key: str, val: str) -> None:
        try:
            flap = float(val)
        except ValueError:
            return

        if flap > 0.9:
            color = self.COLOR["red"]
        elif flap >= 0.5:
            color = self.COLOR["yellow"]
        elif flap >= 0.1:
            color = self.COLOR["green"]
        else:
            color = self.COLOR["off"]

        self.midi_out.sendNoteOn(0, self.FLAPS_LED_ID, color)

    # -------------------------------------------------------
    # CONFIG LOADING
    # -------------------------------------------------------

    def loadConfigData(self, cfg: Any, midiClientItf) -> None:
        self.midi = midiClientItf

        midi_input = FlightgearMidi.DataConfigMidiInput()
        midi_input.midiInputIdx = 0
        midi_input.midiInputName = "FlightgearOut"

        logger.info("Available MIDI input ports:\n%s",
                    "\n".join(" " + p for p in self.midi.getInPorts()))
        logger.info("Available MIDI output ports:\n%s",
                    "\n".join(" " + p for p in self.midi.getOutPorts()))

        if not self.midi.openLibreMidiOutPort("FlightgearIn", 0):
            logger.error("Failed to open MIDI output port.")
            sys.exit(1)

        self.midi_out = self.midi.getLibreMidiOutPort("FlightgearIn", 0)

        # Initialize LEDs
        for led in (self.FLAPS_LED_ID, self.AIR_SPEED_LED_ID):
            self.midi_out.sendNoteOn(0, led, self.COLOR["off"])

        # Subclass must define mappings
        self.set_mappings()

        # Apply bindings
        apply_midi_bindings(
            cfg.dataConfigPullerFgKeys,
            midi_input,
            self.on_off_toggle,
            self.pull_on_off,
            self.mappings,
            self.toggle_mappings,
            self.puller_mappings,
        )

        cfg.dataConfigMidiInputs.append(midi_input)
        self.midi.setDataConfig(cfg)
