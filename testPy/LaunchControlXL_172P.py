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
        # PULLER (FG → MIDI LED) MAPPINGS
        # -------------------------------------------------------
        self.puller_mappings = [
            ("/controls/flight/flaps", self.FLAPS_LED_ID, self.flaps_on),
            ("/instrumentation/airspeed-indicator/indicated-speed-kt",
            self.AIR_SPEED_LED_ID, self.pull_indicated_air_speed),
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
