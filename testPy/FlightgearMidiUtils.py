from FlightgearMidiHelper import (    
    FlightgearMidi
)

# ---------------------------------------------------------------------------
# CONFIG HELPERS
# ---------------------------------------------------------------------------

def add_mapping(
    midi_input: FlightgearMidi.DataConfigMidiInput,
    from_start: int,
    from_end: int,
    to_start: int,
    to_end: int,
    msg_type: int,
    channel: int,
    cc: int,
    cmd: str,
) -> None:
    """Create and append a single MIDI→Telnet mapping."""
    m = FlightgearMidi.DataConfigFromMidiToTelnet()
    m.fromStart = from_start
    m.fromEnd = from_end
    m.toStart = to_start
    m.toEnd = to_end
    m.midiMsgType = msg_type
    m.midiChannel = channel
    m.notePitchOrCcChannel = cc
    m.setCmd = cmd
    midi_input.dataConfigFromMidiToTelnets.append(m)


def add_mappings(
    midi_input: FlightgearMidi.DataConfigMidiInput,
    mappings: Iterable[Tuple[Any, ...]],
) -> None:
    """Add multiple MIDI→Telnet mappings."""
    for args in mappings:
        add_mapping(midi_input, *args)




def add_callback_mappings(midi_input: FlightgearMidi.DataConfigMidiInput,
    callback_mappings: Any) -> None:
    for midiMsgType, notePitchOrCcChannel, callback in callback_mappings:
        itm = FlightgearMidi.DataConfigFromMidiToTelnet()
        itm.midiMsgType = midiMsgType
        itm.notePitchOrCcChannel = notePitchOrCcChannel
        itm.isCallback = True
        itm.callback = callback
        midi_input.dataConfigFromMidiToTelnets.append(itm)        

def add_pullers(
    puller_list: list,
    pullers: Iterable[Tuple[str, Any]],
) -> None:
    """Add FG→callback pullers."""
    for path, cb in pullers:
        p = FlightgearMidi.DataConfigPullerFgKey()
        p.fgKetPath = path
        p.callback = cb
        puller_list.append(p)

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

def build_callback_mappings(toggle_mappings, toggle_callback):
    result = []
    for midiMsgType, led_id, property_path in toggle_mappings:

        # Build callback using the device-specific function
        def cb(val, property_path=property_path):
            toggle_callback(property_path, val)

        result.append((midiMsgType, led_id, cb))
    return result


def build_and_callback_mappings(midi_input, toggle_mappings, toggle_callback):
    mappings = build_callback_mappings(toggle_mappings, toggle_callback)
    add_callback_mappings(midi_input, mappings)




def build_pullers(puller_mappings, pull_on_off_callback):
    result = []
    for property_path, led_id, callback in puller_mappings:

        # Wrap correctly depending on callback type
        def cb(key, val, callback=callback, led_id=led_id):
            if callback is pull_on_off_callback:
                # needs led_id as first arg
                callback(led_id, key, val)
            else:
                # plain (key, val) callback
                callback(key, val)

        result.append((property_path, cb))

    return result


def build_and_callback_pullers(dataConfigPullerFgKeys, puller_mappings, toggle_mappings, pull_on_off_callback):
    # Auto-append pullers from toggle mappings, using pull_on_off_callback
    for _, led_id, property_path in toggle_mappings:
        puller_mappings.append((property_path, led_id, pull_on_off_callback))

    pullers = build_pullers(puller_mappings, pull_on_off_callback)
    add_pullers(dataConfigPullerFgKeys, pullers)


