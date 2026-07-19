from FlightgearMidiHelper import (
    FlightgearMidi
)

from typing import Any, Iterable, Tuple, Callable, List

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
    for args in mappings:
        add_mapping(midi_input, *args)


def add_callback_mappings(
    midi_input: FlightgearMidi.DataConfigMidiInput,
    callback_mappings: Any,
) -> None:
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
    for path, cb in pullers:
        p = FlightgearMidi.DataConfigPullerFgKey()
        p.fgKetPath = path
        p.callback = cb
        puller_list.append(p)

# ---------------------------------------------------------------------------
# CALLBACK BUILDERS
# ---------------------------------------------------------------------------

def build_callback_mappings(
    toggle_mappings: Iterable[Tuple[Any, Any, str]],
    toggle_callback: Callable[[str, Any], None],
) -> List[Tuple[Any, Any, Callable[[Any], None]]]:
    result = []

    for midiMsgType, led_id, property_path in toggle_mappings:

        def cb(val, property_path=property_path):
            toggle_callback(property_path, val)

        result.append((midiMsgType, led_id, cb))

    return result


def build_and_callback_mappings(
    midi_input: FlightgearMidi.DataConfigMidiInput,
    toggle_mappings: Iterable[Tuple[Any, Any, str]],
    toggle_callback: Callable[[str, Any], None],
) -> None:
    mappings = build_callback_mappings(toggle_mappings, toggle_callback)
    add_callback_mappings(midi_input, mappings)


def build_pullers(
    puller_mappings: Iterable[Tuple[str, int, Callable]],
    pull_on_off_callback: Callable[[int, str, Any], None],
):
    result = []
    for property_path, led_id, callback in puller_mappings:

        def cb(key, val, callback=callback, led_id=led_id):
            if callback is pull_on_off_callback:
                callback(led_id, key, val)
            else:
                callback(key, val)

        result.append((property_path, cb))

    return result


def build_and_callback_pullers(
    dataConfigPullerFgKeys: list,
    puller_mappings: List[Tuple[str, int, Callable]],
    toggle_mappings: Iterable[Tuple[Any, int, str]],
    pull_on_off_callback: Callable[[int, str, Any], None],
) -> None:
    for _, led_id, property_path in toggle_mappings:
        puller_mappings.append((property_path, led_id, pull_on_off_callback))

    pullers = build_pullers(puller_mappings, pull_on_off_callback)
    add_pullers(dataConfigPullerFgKeys, pullers)

def apply_midi_bindings(cfg: FlightgearMidi.DataConfig,
                        midi_input: FlightgearMidi.DataConfigMidiInput,
                        ctrl: LaunchControlXL,
                        mappings,
                        toggle_mappings,
                        puller_mappings) -> None:

    # Standard CC mappings
    add_mappings(midi_input, mappings)

    # Toggle buttons
    build_and_callback_mappings(
        midi_input,
        toggle_mappings,
        ctrl.on_off_toggle
    )

    # Pullers
    build_and_callback_pullers(
        cfg.dataConfigPullerFgKeys,
        puller_mappings,
        toggle_mappings,
        ctrl.pull_on_off,
    )