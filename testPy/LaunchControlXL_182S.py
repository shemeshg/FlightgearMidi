from dataclasses import dataclass
from FgLibHelpers.FlightgearMidiHelper import main_loop, FlightgearMidi, logger
from FgLibHelpers.LaunchControlXLAll import LaunchControlXLAll


@dataclass
class LaunchControlXL(LaunchControlXLAll):

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

            # prop pitch
            (0, 127, 0, 1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 83,
             "/controls/engines/engine[0]/propeller-pitch"),

            # mixture
            (0, 127, 0, 1, FlightgearMidi.MidiMsgType.CONTROL_CHANGE, -1, 84,
             "/controls/engines/engine[0]/mixture"),
        ]

        # -------------------------------------------------------
        # TOGGLE BUTTON MAPPINGS
        # -------------------------------------------------------
        self.toggle_mappings = [
            (FlightgearMidi.MidiMsgType.NOTE_ON, self.LANDING_LIGHTS_LED_ID,
             "/controls/lighting/landing-lights"),

            (FlightgearMidi.MidiMsgType.NOTE_ON, self.TAXI_LIGHT_LED_ID,
             "/controls/lighting/taxi-light"),
        ]

        # -------------------------------------------------------
        # DECLARATIVE PULLER TABLE (CLASS ATTRIBUTE!)
        # -------------------------------------------------------

        self.puller_config  = {
                "/orientation/roll-deg": {
                    "led_id": self.ROLL_DEG_ID,
                    "use_abs": True,
                    "track_previous": True,
                    "thresholds": [
                        (lambda v: v < 35, "off"),
                        (lambda v: v < 45, "yellow"),
                        (lambda v: True, "red"),
                    ],
                },

                "/instrumentation/airspeed-indicator/indicated-speed-kt": {
                    "led_id": self.AIR_SPEED_LED_ID,
                    "use_abs": False,
                    "track_previous": True,
                    "thresholds": [
                        (lambda v: v > 70, "off"),
                        (lambda v: v >= 50, "green"),
                        (lambda v: v >= 40, "yellow"),
                        (lambda v: True, "red"),
                    ],
                },

                "/controls/flight/flaps": {
                    "led_id": self.FLAPS_LED_ID,
                    "use_abs": False,
                    "track_previous": False,
                    "thresholds": [
                        (lambda v: v > 0.9, "red"),
                        (lambda v: v >= 0.5, "yellow"),
                        (lambda v: v >= 0.1, "green"),
                        (lambda v: True, "off"),
                    ],
                },
            }


        # -------------------------------------------------------
        # PULLER (FG → MIDI LED) MAPPINGS
        # -------------------------------------------------------
        # All pullers now use pull_generic() and the declarative PULLER_CONFIG table
        self.puller_mappings = [
            ("/controls/flight/flaps", self.FLAPS_LED_ID, self.pull_generic),
            ("/instrumentation/airspeed-indicator/indicated-speed-kt",
             self.AIR_SPEED_LED_ID, self.pull_generic),
            ("/orientation/roll-deg",
             self.ROLL_DEG_ID, self.pull_generic),
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
