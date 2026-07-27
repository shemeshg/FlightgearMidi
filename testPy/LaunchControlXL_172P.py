from dataclasses import dataclass
from FgLibHelpers.FlightgearMidiHelper import main_loop, FlightgearMidi, logger
from FgLibHelpers.LaunchControlXLAll import LaunchControlXLAll
from FgLibHelpers.FlightgearMidiUtils import pull_generic


@dataclass
class LaunchControlXL(LaunchControlXLAll):

    def pull_generic_wrapper(self, key, val):
        pull_generic(
            self.midi_out,
            self.previous_colors,
            self.puller_config,
            key,
            val
        )

    def set_mappings(self):
        """
        Define all MIDI → FlightGear bindings for this aircraft.
        Cleaner, safer, and easier to maintain.
        """

        # -------------------------------------------------------
        # AXIS / CONTROL CHANGE MAPPINGS
        # -------------------------------------------------------
        self.mappings = [
            # throttle
            (0, 127, 0, 1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 77,
             "/controls/engines/engine[0]/throttle"),

            # rudder
            (0, 127, 1, -1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 78,
             "/controls/flight/rudder"),

            # aileron
            (0, 127, 1, -1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 79,
             "/controls/flight/aileron"),

            # elevator
            (0, 127, -1, 1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 80,
             "/controls/flight/elevator"),

            # mixture
            (0, 127, 0, 1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 84,
             "/controls/engines/current-engine/mixture"),
        ]

        # -------------------------------------------------------
        # TOGGLE BUTTON MAPPINGS
        # -------------------------------------------------------
        self.toggle_mappings = [
            (FlightgearMidi.MidiMsgType.NOTE_ON, self.CARB_HEAT_LED_ID,
             "/controls/engines/current-engine/carb-heat"),

            (FlightgearMidi.MidiMsgType.NOTE_ON, self.LANDING_LIGHTS_LED_ID,
             "/controls/lighting/landing-lights"),

            (FlightgearMidi.MidiMsgType.NOTE_ON, self.TAXI_LIGHT_LED_ID,
             "/controls/lighting/taxi-light"),
        ]

        # -------------------------------------------------------
        # DECLARATIVE PULLER TABLE (DIRECT COLOR VALUES)
        # -------------------------------------------------------

        self.puller_config = {
            "/orientation/roll-deg": {
                "led_id": self.ROLL_DEG_ID,
                "use_abs": True,
                "track_previous": True,
                "thresholds": [
                    (lambda v: v < 35, self.COLOR["off"]),
                    (lambda v: v < 45, self.COLOR["yellow"]),
                    (lambda v: True, self.COLOR["red"]),
                ],
            },

            "/instrumentation/airspeed-indicator/indicated-speed-kt": {
                "led_id": self.AIR_SPEED_LED_ID,
                "use_abs": False,
                "track_previous": True,
                "thresholds": [
                    (lambda v: v > 70, self.COLOR["off"]),
                    (lambda v: v >= 50, self.COLOR["green"]),
                    (lambda v: v >= 40, self.COLOR["yellow"]),
                    (lambda v: True, self.COLOR["red"]),
                ],
            },

            "/controls/flight/flaps": {
                "led_id": self.FLAPS_LED_ID,
                "use_abs": False,
                "track_previous": False,
                "thresholds": [
                    (lambda v: v > 0.9, self.COLOR["red"]),
                    (lambda v: v >= 0.5, self.COLOR["yellow"]),
                    (lambda v: v >= 0.1, self.COLOR["green"]),
                    (lambda v: True, self.COLOR["off"]),
                ],
            },
        }

        # -------------------------------------------------------
        # PULLER (FG → MIDI LED) MAPPINGS
        # -------------------------------------------------------
        self.puller_mappings = [
            ("/controls/flight/flaps", self.FLAPS_LED_ID, self.pull_generic_wrapper),
            ("/instrumentation/airspeed-indicator/indicated-speed-kt",
             self.AIR_SPEED_LED_ID, self.pull_generic_wrapper),
            ("/orientation/roll-deg",
             self.ROLL_DEG_ID, self.pull_generic_wrapper),
        ]


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
