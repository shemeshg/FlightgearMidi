from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
import sys

from .FlightgearMidiUtils import apply_midi_bindings
from .FlightgearMidiHelper import FlightgearMidi, logger


# ---------------------------------------------------------------------------
# DEVICE CLASS
# ---------------------------------------------------------------------------

@dataclass
class LaunchControlXLAll:
    midi: Optional[Any] = None
    midi_out: Optional[Any] = None


    

    # Store previous LED colors by LED ID
    previous_colors: Dict[int, Optional[int]] = field(default_factory=dict)

    toggle_states: Dict[str, bool] = field(default_factory=dict)

    mappings: List[Any] = field(default_factory=list)
    toggle_mappings: List[Any] = field(default_factory=list)
    puller_mappings: List[Any] = field(default_factory=list)
    puller_config: Optional[Any] = None

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
    ROLL_DEG_ID = 74

    CARB_HEAT_LED_ID = 105
    LANDING_LIGHTS_LED_ID = 106
    TAXI_LIGHT_LED_ID = 107


    # -------------------------------------------------------
    # ABSTRACT METHOD
    # -------------------------------------------------------

    def set_mappings(self) -> None:
        raise NotImplementedError("set_mappings() must be implemented in subclass")

    # -------------------------------------------------------
    # LED UPDATE HELPER
    # -------------------------------------------------------

    def _update_led(
        self,
        raw_val: str,
        thresholds: list,
        led_id: int,
        use_abs: bool = False,
        track_previous: bool = True,
    ):
        try:
            val = float(raw_val)
            if use_abs:
                val = abs(val)
        except ValueError:
            return

        for cond, color_key in thresholds:
            if cond(val):
                color = self.COLOR[color_key]
                break

        if track_previous:
            prev_color = self.previous_colors.get(led_id)
            if color != prev_color:
                self.previous_colors[led_id] = color
                self.midi_out.sendNoteOn(0, led_id, color)
        else:
            self.midi_out.sendNoteOn(0, led_id, color)

    # -------------------------------------------------------
    # GENERIC PULLER
    # -------------------------------------------------------

    def pull_generic(self, key: str, val: str) -> None:
        cfg = self.puller_config.get(key)
        if not cfg:
            return

        self._update_led(
            raw_val=val,
            thresholds=cfg["thresholds"],
            led_id=cfg["led_id"],
            use_abs=cfg["use_abs"],
            track_previous=cfg["track_previous"],
        )

    # -------------------------------------------------------
    # OTHER CALLBACKS
    # -------------------------------------------------------

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
        )

        cfg.dataConfigMidiInputs.append(midi_input)
        self.midi.setDataConfig(cfg)
