from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
import sys

from .FlightgearMidiUtils import apply_midi_bindings
from .FlightgearMidiHelper import FlightgearMidi


from FgLibHelpers.FlightgearMidiUtils import pull_generic


@dataclass
class LaunchControlXLAll:
    midi: Optional[Any] = None
    midi_out: Optional[Any] = None

    previous_colors: Dict[int, Optional[int]] = field(default_factory=dict)
    toggle_states: Dict[str, bool] = field(default_factory=dict)

    mappings: List[Any] = field(default_factory=list)
    toggle_mappings: List[Any] = field(default_factory=list)
    puller_mappings: List[Any] = field(default_factory=list)
    puller_config: Optional[Any] = None

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
    ROLL_DEG_ID = 74

    CARB_HEAT_LED_ID = 105
    LANDING_LIGHTS_LED_ID = 106
    TAXI_LIGHT_LED_ID = 107

    def set_mappings(self):
        raise NotImplementedError

    def pull_generic_wrapper(self, key, val):
        pull_generic(self.midi_out, self.previous_colors,
                     self.puller_config, key, val)

    def pull_on_off(self, btn_id, key, val):
        v = val.strip().lower().replace('"', '')
        if v not in ("true", "false"):
            return
        is_on = (v == "true")
        self.midi_out.sendNoteOn(
            0, btn_id,
            self.COLOR["high"] if is_on else self.COLOR["low"]
        )

    def on_off_toggle(self, key, val):
        new_state = not self.toggle_states.get(key, False)
        self.toggle_states[key] = new_state
        self.midi.sendTerminalRaw(f"set {key} {'true' if new_state else 'false'}")

    def loadConfigData(self, cfg, midiClientItf):
        self.midi = midiClientItf

        midi_input = FlightgearMidi.DataConfigMidiInput()
        midi_input.midiInputIdx = 0
        midi_input.midiInputName = "FlightgearOut"

        if not self.midi.openLibreMidiOutPort("FlightgearIn", 0):
            sys.exit(1)

        self.midi_out = self.midi.getLibreMidiOutPort("FlightgearIn", 0)

        for led in (self.FLAPS_LED_ID, self.AIR_SPEED_LED_ID):
            self.midi_out.sendNoteOn(0, led, self.COLOR["off"])

        self.set_mappings()

        apply_midi_bindings(
            cfg.dataConfigPullerFgKeys,
            midi_input,
            self.on_off_toggle,
            self.pull_on_off,
            self.mappings,
            self.toggle_mappings,
            self.puller_mappings,
            self.puller_config,
            self.pull_generic_wrapper,
        )

        cfg.dataConfigMidiInputs.append(midi_input)
        self.midi.setDataConfig(cfg)
