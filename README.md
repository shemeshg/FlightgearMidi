# 🎹 FlightgearMidi — Python MIDI → FlightGear Bridge  
A lightweight C++/pybind11 module with a Python API

This project provides a Python‑friendly interface for configuring MIDI input mappings and FlightGear telnet output.  
The core logic is implemented in C++ for performance, and exposed to Python using **pybind11**.  
You write your automation logic in Python — the C++ backend handles MIDI, telnet, and real‑time routing.

---

## 📦 Features

- Python API for all configuration objects (`DataConfig`, `DataConfigMidiInput`, etc.)
- Real‑time MIDI → FlightGear telnet mapping
- Python callbacks for FlightGear value changes
- Simple configuration builder (see `testPy/test.py`)
- Cross‑platform C++ backend

---

# 🛠️ Building the Python Module

enable `telnet` on `Flightgear`

Settings->additional settings

```
--telnet=5500 --prop:/sim/terrasync/http-server=http://flightgear.sourceforge.net/scenery
```

### 1. Install dependencies

You need:

- CMake (3.16+)
- A C++17 compiler
- Python 3.10+ (or your preferred version)
- pybind11
- boost

On macOS:

```bash
brew install cmake pybind11 boost
```

on linux
```bash
sudo apt-get update && sudo apt-get install libboost-all-dev
```


Optional: create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 2. Configure and build

From the project root:

```bash
mkdir build
cd build
cmake ..
make -j
```
or

```
python3 -m venv .venv
source .venv/bin/activate
pip install build
python -m build --wheel 
```

This produces a Python extension module:

```
FlightgearMidi.cpython-311-darwin.so
```

(or similar, depending on your Python version)

---

### 3. Make Python able to import the module

Option A — copy the module into your virtualenv:

```bash
cp FlightgearMidi*.so ../.venv/lib/python3.11/site-packages/
```

Option B — add the build directory to `sys.path` inside your script:

```python
import sys
sys.path.append("/path/to/FlightgearMidi/build")
import FlightgearMidi
```

---

# 🧪 Running the Test Script

The example script is located at:

```
testPy/test.py
```

It demonstrates:

- Creating a `DataConfig`
- Adding MIDI input mappings
- Adding FlightGear puller keys
- Assigning Python callbacks
- Starting the MIDI client
- Printing incoming/outgoing values

### Run it:

```bash
python3 testPy/test.py
```

---

# 📘 Understanding the Test Script

The script builds a full configuration in Python:

### 1. Create the main config object

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

Each mapping defines:

- MIDI range (`fromStart`, `fromEnd`)
- FlightGear range (`toStart`, `toEnd`)
- MIDI message type
- MIDI channel / CC number
- FlightGear command path

Example:

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

### 4. Add FlightGear puller keys with Python callbacks

```python
pull = FlightgearMidi.DataConfigPullerFgKey()
pull.fgKetPath = "/controls/flight/rudder"
pull.callback = lambda key, val: print(f"FG update: {key} = {val}")

cfg.dataConfigPullerFgKeys.append(pull)
```

### 5. Send the config to the C++ backend

```python
midi = FlightgearMidi.getMidiClientItf()
midi.setDataConfig(cfg)
```

### 6. Start the MIDI client

```python
midi.startMidiClient()
```

The backend now:

- Reads MIDI input
- Converts values according to your config
- Sends commands to FlightGear via telnet
- Calls your Python callbacks with FG values on interval

---

# 🎯 Summary

This project gives you a fast C++ backend with a clean Python API:

- Build the module with CMake  
- Import `FlightgearMidi` in Python  
- Construct your config  
- Start the MIDI client  
- Enjoy real‑time MIDI → FlightGear control  

