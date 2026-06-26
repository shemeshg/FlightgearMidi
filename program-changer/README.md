# FlightGear MIDI Bridge

A lightweight tool that connects **MIDI controllers** to **FlightGear** via its
built‑in **telnet property interface**.  
The goal is to provide a flexible, YAML‑driven mapping system where:

- MIDI → FlightGear (control aircraft)
- FlightGear → MIDI (feedback to knobs, LEDs, motorized faders)
- Macros (multi‑command sequences)
- Value transforms (range mapping, rounding, clamping)
- Presets (enable/disable groups of mappings)

The project is still in early development, but the configuration format is already
taking shape.

---

## Features (planned / partially implemented)

- **MIDI input**
  - CC, Note On/Off, channel filtering
  - Per‑mapping transforms (range, rounding, scaling)
  - Macros with delays
  - Preset‑based activation

- **MIDI output**
  - Send CC/Note messages based on FlightGear property changes
  - Useful for LED rings, motorized faders, or visual feedback

- **FlightGear telnet**
  - Connects to FG’s property tree (`set /path value`)
  - Auto‑reconnect after FlightGear restarts (Shift+Esc)
  - Optional polling for property updates (“follow” mode)

- **YAML configuration**
  - Human‑readable
  - Declarative mapping rules
  - Easy to extend

---

## Example Configuration

### Telnet

```yaml
telnet:
  host: "localhost"
  port: 5500
  connect_on_start: true
  reconnect: true
  reconnect_delay: 2000
  read_interval: 50
  command_prefix: ""
  command_suffix: "\n"
  debug: false

  inbound:
    - id: mixture_feedback
      property: "/controls/engines/engine[0]/mixture"
      transform:
        from: [0, 1]
        to: [0, 127]
        round: 0
      midi_out:
        port: "Launch Control XL"
        type: control_change
        control: 77
```

This listens for FlightGear sending:

```
/controls/engines/engine[0]/mixture 0.8
```

…and converts it into a MIDI CC message.

---

### MIDI Input

```yaml
midi:
  ports:
    - name: "Launch Control XL"
      index: 0
      mappings:
        - id: throttle
          presets: [selected_1]
          match:
            type: control_change
            control: 77
          transform:
            from: [0, 127]
            to: [0, 1]
            round: 3
          command: "set /controls/engines/engine/throttle ${throttle}"

        - id: engine_start_macro
          match:
            type: note_on
            note: 40
          macro:
            - command: "set /controls/engines/engine[0]/starter 1"
            - command: "set /controls/engines/engine[0]/mixture 1"
            - command: "set /controls/engines/engine[0]/throttle 0.2"
            - delay: 500
            - command: "set /controls/engines/engine[0]/starter 0"
```

---

## Presets

```yaml
presets:
  selected_1:
    active: true
```

Presets allow enabling/disabling groups of mappings without editing them.

---

## Build Status

> ⚠️ **Early development**  
> Not all features are implemented yet.  
> Expect breaking changes.

---

## Goals

- Zero‑latency MIDI → FG control
- Smooth feedback loops (FG → MIDI)
- Clean YAML configuration
- Robust telnet handling (no hangs after FG crash/restart)
- Cross‑platform (Linux/Windows/macOS)

---

## License

MIT (or whatever you choose)

---

## Contributing

Issues, ideas, and pull requests are welcome once the core stabilizes.

