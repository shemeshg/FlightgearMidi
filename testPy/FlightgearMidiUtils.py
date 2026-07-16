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