# 🎹 FlightgearMidi — Fast MIDI ↔ FlightGear Bridge  
A lightweight C++ backend with a clean Python API

**FlightgearMidi** connects MIDI controllers to FlightGear’s telnet interface.  
You write automation logic in Python; the C++ layer handles:

- MIDI input  
- MIDI output  
- FlightGear send telnet commands  
- FlightGear receive http get commands  
- Real‑time routing and callbacks  

This gives you **low‑latency control** of aircraft systems using any MIDI device.

---

## ✨ Features

- Python API for all configuration objects (`DataConfig`, `DataConfigMidiInput`, etc.)
- Real‑time MIDI → FlightGear mapping
- Python callbacks for FlightGear value updates
- MIDI output (LEDs, feedback, etc.)
- Cross‑platform C++ backend via **pybind11**
- Example scripts included

---

# 🛠 Installation

## 1. Enable FlightGear telnet

Add this to FlightGear’s *Additional Settings*:

```
--telnet=5500 --httpd=8800
```

---

## 2. Install FlightgearMidi

### Option A — Install from GitHub Releases (recommended)

1. Go to the repository’s **Releases** page  
2. Download the wheel matching your OS + Python version  
3. Install it:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install ./flightgearmidi‑0.1.0‑cp311‑cp311‑macosx_13_0_arm64.whl
```

Then:

```python
import FlightgearMidi
```

---

### Option B — Build from source

#### Requirements

- CMake ≥ 3.16  
- C++17 compiler  
- Python ≥ 3.10  
- `pip install meason`



#### Build

```bash
mkdir build
cd build
cmake ..
make -j
```

This produces:

```
FlightgearMidi.cpython-311-darwin.so
```

#### Install manually

```bash
cp FlightgearMidi*.so ../.venv/lib/python3.11/site-packages/
```

or add the build directory:

```python
import sys
sys.path.append("/path/to/FlightgearMidi/build")
import FlightgearMidi
```

---

# 🧪 Example

Simplified example script: [https://github.com/shemeshg/FlightgearMidi/blob/main/testPy/test.py](https://github.com/shemeshg/FlightgearMidi/blob/main/testPy/test.py)

Complete example: [https://github.com/shemeshg/FlightgearMidi/blob/main/testPy/LaunchControlXL_172P.py](https://github.com/shemeshg/FlightgearMidi/blob/main/testPy/LaunchControlXL_172P.py)


Run it:

```bash
python3 testPy/test.py
```

---

# 📘 Quick Start

### 1. Create a config

```python
cfg = FlightgearMidi.DataConfig()
cfg.telnetHost = "localhost"
cfg.telnetPort = "5500"
cfg.httpdPort = "8800"
```

### 2. Add a MIDI input

```python
midi_input = FlightgearMidi.DataConfigMidiInput()
midi_input.midiInputIdx = 0
midi_input.midiInputName = "Launch Control XL"
```

### 3. Add MIDI → FlightGear mappings

```python
mapping = FlightgearMidi.DataConfigFromMidiToTelnet()
mapping.fromStart = 0
mapping.fromEnd = 127
mapping.toStart = 0
mapping.toEnd = 1
mapping.midiMsgType = FlightgearMidi.MidiMsgType.CONTROL_CHANGE
mapping.notePitchOrCcChannel = 77
mapping.setCmd = "/controls/engines/engine[0]/throttle"

midi_input.dataConfigFromMidiToTelnets.append(mapping)
```

### 4. Add a callback mapping

```python
carb_heat = FlightgearMidi.DataConfigFromMidiToTelnet()
carb_heat.midiMsgType = FlightgearMidi.MidiMsgType.NOTE_ON
carb_heat.notePitchOrCcChannel = 105
carb_heat.isCallback = True
carb_heat.callback = lambda val: print("Carb heat toggled:", val)

midi_input.dataConfigFromMidiToTelnets.append(carb_heat)
```

### 5. Add FlightGear puller keys

```python
pull = FlightgearMidi.DataConfigPullerFgKey()
pull.fgKetPath = "/controls/flight/rudder"
pull.callback = lambda key, val: print("FG update:", key, val)

cfg.dataConfigPullerFgKeys.append(pull)
```

### 6. Send config to backend

```python
midi = FlightgearMidi.getMidiClientItf()
midi.setDataConfig(cfg)
```

### 7. Start MIDI client

```python
midi.startMidiClient()
```

### 8. Send MIDI output

```python
midiOut = midi.getLibreMidiOutPort("Flightgear", 0)
midiOut.sendNoteOn(0, 73, 60)
```

---

# 🎯 Summary

**FlightgearMidi** gives you:

- A fast C++ backend  
- A simple Python API  
- Real‑time MIDI → FlightGear control  
- Easy callback handling  
- Clean configuration objects  

Build locally or install from Releases, write your mappings in Python, and let the C++ backend handle the real‑time work.

