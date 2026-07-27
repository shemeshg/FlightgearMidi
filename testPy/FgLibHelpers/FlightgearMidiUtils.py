from .FlightgearMidiHelper import FlightgearMidi
from typing import Any, Iterable, Tuple, Callable, List

# ---------------------------------------------------------------------------
# CONFIG HELPERS
# ---------------------------------------------------------------------------

def add_mapping(midi_input, from_start, from_end, to_start, to_end,
                msg_type, channel, cc, cmd):
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


def add_mappings(midi_input, mappings):
    for args in mappings:
        add_mapping(midi_input, *args)


def add_callback_mappings(midi_input, callback_mappings):
    for midiMsgType, notePitchOrCcChannel, callback in callback_mappings:
        itm = FlightgearMidi.DataConfigFromMidiToTelnet()
        itm.midiMsgType = midiMsgType
        itm.notePitchOrCcChannel = notePitchOrCcChannel
        itm.isCallback = True
        itm.callback = callback
        midi_input.dataConfigFromMidiToTelnets.append(itm)


def add_pullers(puller_list, pullers):
    for path, cb in pullers:
        p = FlightgearMidi.DataConfigPullerFgKey()
        p.fgKetPath = path
        p.callback = cb
        puller_list.append(p)

# ---------------------------------------------------------------------------
# CALLBACK BUILDERS
# ---------------------------------------------------------------------------

def build_callback_mappings(toggle_mappings, toggle_callback):
    result = []
    for midiMsgType, led_id, property_path in toggle_mappings:

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

        def cb(key, val, callback=callback, led_id=led_id):
            if callback is pull_on_off_callback:
                callback(led_id, key, val)
            else:
                callback(key, val)

        result.append((property_path, cb))
    return result


def build_and_callback_pullers(dataConfigPullerFgKeys,
                               puller_mappings,
                               toggle_mappings,
                               pull_on_off_callback):

    for _, led_id, property_path in toggle_mappings:
        puller_mappings.append((property_path, led_id, pull_on_off_callback))

    pullers = build_pullers(puller_mappings, pull_on_off_callback)
    add_pullers(dataConfigPullerFgKeys, pullers)


def apply_midi_bindings(dataConfigPullerFgKeys,
                        midi_input,
                        on_off_toggle,
                        pull_on_off,
                        mappings,
                        toggle_mappings,
                        puller_mappings):

    add_mappings(midi_input, mappings)

    build_and_callback_mappings(
        midi_input,
        toggle_mappings,
        on_off_toggle
    )

    build_and_callback_pullers(
        dataConfigPullerFgKeys,
        puller_mappings,
        toggle_mappings,
        pull_on_off,
    )

# ---------------------------------------------------------------------------
# PURE LED LOGIC
# ---------------------------------------------------------------------------

def update_led(midi_out, previous_colors, raw_val, thresholds,
               led_id, use_abs=False, track_previous=True):

    try:
        val = float(raw_val)
        if use_abs:
            val = abs(val)
    except ValueError:
        return

    for cond, color in thresholds:
        if cond(val):
            break

    if track_previous:
        prev_color = previous_colors.get(led_id)
        if color != prev_color:
            previous_colors[led_id] = color
            midi_out.sendNoteOn(0, led_id, color)
    else:
        midi_out.sendNoteOn(0, led_id, color)


def pull_generic(midi_out, previous_colors, puller_config, key, val):
    cfg = puller_config.get(key)
    if not cfg:
        return

    update_led(
        midi_out,
        previous_colors,
        raw_val=val,
        thresholds=cfg["thresholds"],
        led_id=cfg["led_id"],
        use_abs=cfg["use_abs"],
        track_previous=cfg["track_previous"],
    )
