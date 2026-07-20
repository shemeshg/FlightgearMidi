from dataclasses import dataclass, field
from typing import Any, Optional
import sys


from FlightgearMidiHelper import (
    main_loop,
    FlightgearMidi,
    logger,
)

from FlightgearMidiUtils import (
    apply_midi_bindings
)

# ---------------------------------------------------------------------------
# DEVICE CLASS (formerly AppState)
# ---------------------------------------------------------------------------

@dataclass
class LaunchControlXL:
    midi: Optional[Any] = None
    midi_out: Optional[Any] = None

    previous_air_speed_color: Optional[int] = None
    toggle_states: dict = field(default_factory=dict)


    # -------------------------------------------------------
    # CONSTANTS (class-level)
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
        "low": 0
    }

    FLAPS_LED_ID = 13 + 16 * 0
    AIR_SPEED_LED_ID = 73

    CARB_HEAT_LED_ID = 105
    LANDING_LIGHTS_LED_ID = 106
    TAXI_LIGHT_LED_ID = 107

    # -------------------------------------------------------
    # CALLBACKS
    # -------------------------------------------------------

    def pull_indicated_air_speed(self, key: str, val: str) -> None:
        try:
            speed = float(val)
        except Exception:
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
        self.midi_out.sendNoteOn(0, btn_id,
                                 self.COLOR["high"] if is_on else self.COLOR["low"])

    def on_off_toggle(self, key: str, val: Any) -> None:
        prev = self.toggle_states.get(key, False)
        new = not prev
        self.toggle_states[key] = new

        cmd = "true" if new else "false"
        self.midi.sendTerminalRaw(f"set {key} {cmd}")

    def flaps_on(self, key: str, val: str) -> None:
        try:
            flap = float(val)
        except Exception:
            return

        if flap > 0.9:
            color = self.COLOR["red"]
        elif flap >= 0.6:
            color = self.COLOR["yellow"]
        elif flap >= 0.1:
            color = self.COLOR["green"]
        else:
            color = self.COLOR["off"]

        self.midi_out.sendNoteOn(0, self.FLAPS_LED_ID, color)


    # ---------------------------------------------------------------------------
    # CONFIG LOADING
    # ---------------------------------------------------------------------------

    def loadConfigData(self, cfg: DataConfig, midiClientItf):

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

        self.midi_out.sendNoteOn(0, self.FLAPS_LED_ID, self.COLOR["off"])
        self.midi_out.sendNoteOn(0, self.AIR_SPEED_LED_ID, self.COLOR["off"])




        # -------------------------------------------------------
        # CONFIGURATION (kept here exactly as you wanted)
        # -------------------------------------------------------

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

        toggle_mappings = [
            (FlightgearMidi.MidiMsgType.NOTE_ON, self.CARB_HEAT_LED_ID,
            "/controls/engines/current-engine/carb-heat"),
            (FlightgearMidi.MidiMsgType.NOTE_ON, self.LANDING_LIGHTS_LED_ID,
            "/controls/lighting/landing-lights"),
            (FlightgearMidi.MidiMsgType.NOTE_ON, self.TAXI_LIGHT_LED_ID,
            "/controls/lighting/taxi-light"),
        ]

        puller_mappings = [
            ("/controls/flight/flaps", self.FLAPS_LED_ID, self.flaps_on),
            ("/instrumentation/airspeed-indicator/indicated-speed-kt",
            self.AIR_SPEED_LED_ID, self.pull_indicated_air_speed),
        ]

        # -------------------------------------------------------
        # APPLY BINDINGS (extracted)
        # -------------------------------------------------------

        apply_midi_bindings(
            cfg,
            midi_input,
            self.on_off_toggle,
            self.pull_on_off,
            mappings,
            toggle_mappings,
            puller_mappings
        )

        cfg.dataConfigMidiInputs.append(midi_input)
        self.midi.setDataConfig(cfg)
        



# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cfg = FlightgearMidi.DataConfig()
    cfg.telnetHost = "localhost"
    cfg.telnetPort = "5500"
    cfg.httpdPort = "8800"

    midiClientItf = FlightgearMidi.getMidiClientItf()
    midiClientItf.pullerSleepInterval = 100

    launchControlXL = LaunchControlXL()
    launchControlXL.loadConfigData(cfg, midiClientItf)
    
    main_loop(midiClientItf)
