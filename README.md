# 🎹 FlightgearMidi — Python MIDI → FlightGear Bridge  
A lightweight C++/pybind11 module with a clean Python API

**FlightgearMidi** maps MIDI input to FlightGear telnet commands using a fast C++ backend exposed to Python via **pybind11**.  
You write automation logic in Python; the C++ layer handles MIDI I/O, telnet communication, and real‑time routing.

*Note:* FlightGear’s telnet interface works best when sending and receiving events are handled in separate scripts threads or DataConfigMidiInput instances.

---

## 📦 Features

- Python API for all configuration objects (`DataConfig`, `DataConfigMidiInput`, etc.)
- Real‑time MIDI → FlightGear telnet mapping
- Python callbacks for FlightGear value updates
- Simple configuration builder (see `testPy/test.py`)
- Cross‑platform C++ backend

---

# 🛠️ Installation

### Enable FlightGear telnet

Add to FlightGear’s *Additional Settings*:

```
--telnet=5500 --prop:/sim/terrasync/http-server=http://flightgear.sourceforge.net/scenery
```

## Option 1 — Install from GitHub Releases (recommended)

You can download a pre‑built wheel from the project’s **GitHub Releases** page.

1. Open the repository’s **Releases** section  
2. Download the `.whl` file matching your OS + Python version  
3. Install it:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install ./flightgearmidi‑0.1.0‑cp311‑cp311‑macosx_13_0_arm64.whl
```

(Replace the filename with the one you downloaded.)

Then simply:

```python
import FlightgearMidi
```

---

## Option 2 — Build the module yourself

### 1. Install dependencies

- CMake ≥ 3.16  
- C++17 compiler  
- Python ≥ 3.10  

Optional virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 2. Build with CMake

```bash
mkdir build
cd build
cmake ..
make -j
```

This produces a Python extension module such as:

```
FlightgearMidi.cpython-311-darwin.so
```

### Alternative: Build via Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install build
python -m build --wheel
cd dist
pip install flightgearmidi-0.1.0-*.whl
```

---

### 3. Make the module importable

**Option A — copy into your virtualenv:**

```bash
cp FlightgearMidi*.so ../.venv/lib/python3.11/site-packages/
```

**Option B — add the build directory to `sys.path`:**

```python
import sys
sys.path.append("/path/to/FlightgearMidi/build")
import FlightgearMidi
```

---

# 🧪 Running the Example

Example script: https://github.com/shemeshg/FlightgearMidi/blob/main/testPy/


```
testPy/test.py
```

It demonstrates:

- Creating a `DataConfig`
- Adding MIDI inputs and mappings
- Adding FlightGear puller keys
- Registering Python callbacks
- Starting the MIDI client
- Sending MIDI output

Run it:

```bash
python3 testPy/test.py
```

---

# 📘 How the Test Script Works

### 1. Create the main config

```python
cfg = FlightgearMidi.DataConfig()
cfg.telnetHost = "localhost"
cfg.telnetPort = "5500"
```

### 2. Add a MIDI input device

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

### 4. Add FlightGear puller keys + callbacks

```python
pull = FlightgearMidi.DataConfigPullerFgKey()
pull.fgKetPath = "/controls/flight/rudder"
pull.callback = lambda key, val: print(f"FG update: {key} = {val}")

cfg.dataConfigPullerFgKeys.append(pull)
```

### 5. Send config to backend

```python
midi = FlightgearMidi.getMidiClientItf()
midi.setDataConfig(cfg)
```

### 6. Start the MIDI client

```python
midi.startMidiClient()
```

### 7. Send MIDI output

```python
if not midi.openLibreMidiOutPort("Flightgear",0):
    print("Forgot to create virtual port")
    print(" out ports:\n" + "\n".join(" " + p for p in midi.getOutPorts()))
    exit(0)

midiOutPort = midi.getLibreMidiOutPort("Flightgear",0)
midiOutPort.sendNoteOn(0, novation_flaps_led_id, novation_color_off)
```

---

# 🎯 Summary

**FlightgearMidi** provides:

- A fast C++ backend  
- A simple Python API  
- Real‑time MIDI → FlightGear control  
- Easy configuration and callback handling  

Install from GitHub Releases or build locally, import the module, define your mappings, and start the MIDI client — everything else runs automatically.

