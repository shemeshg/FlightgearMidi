# **SBOM.md**

## **Software Bill of Materials (SBOM)**  
Project: **FlightgearMidi**  
Repository: [https://github.com/shemeshg/FlightgearMidi](https://github.com/shemeshg/FlightgearMidi)  
Generated: 2026‑07‑10  
Format: SPDX‑lite (human‑readable)

---

## **1. Project Summary**

**FlightgearMidi** is a C++/Python module that bridges MIDI input to FlightGear’s telnet and HTTP property interfaces.  
It uses:

- A C++17 backend  
- Python bindings via **pybind11**  
- MIDI I/O via **libremidi**  
- Signal/slot dispatch via **sigslot**  
- HTTP client via **CPR**  
- JSON parsing via **nlohmann/json**  
- Build tooling via **Meson** (required by libpsl/curl on macOS & Windows)  
- Python packaging via **scikit‑build‑core**

Source structure:  
- `FlightgearMidi/` (C++ backend)  
- `MyLib/` (supporting C++ code)  
- `testPy/` (Python example)  
- `CMakeLists.txt`  
- `pyproject.toml`  

---

## **2. Third‑Party Components**

### **2.1 libremidi**
- **Source:** FetchContent  
- **Repo:** [https://github.com/celtera/libremidi](https://github.com/celtera/libremidi)  
- **Version:** master  
- **License:** MIT  
- **SPDX ID:** MIT  
- **Purpose:** Cross‑platform MIDI input/output.

---

### **2.2 sigslot**
- **Source:** FetchContent  
- **Repo:** [https://github.com/palacaze/sigslot](https://github.com/palacaze/sigslot)  
- **Version:** master  
- **License:** MIT  
- **SPDX ID:** MIT  
- **Purpose:** Lightweight signal/slot mechanism.

---

### **2.3 pybind11**
- **Source:** FetchContent  
- **Repo:** [https://github.com/pybind/pybind11](https://github.com/pybind/pybind11)  
- **Version:** v2.12.0  
- **License:** BSD‑3‑Clause  
- **SPDX ID:** BSD-3-Clause  
- **Purpose:** Python bindings for C++.

---

### **2.4 scikit‑build‑core**
- **Source:** Python build backend  
- **Version:** pip‑resolved  
- **License:** MIT  
- **SPDX ID:** MIT  
- **Purpose:** Modern Python build backend integrating CMake.

---

### **2.5 CPR (C++ Requests)**
- **Source:** FetchContent  
- **Repo:** [https://github.com/libcpr/cpr](https://github.com/libcpr/cpr)  
- **Version:** master  
- **License:** MIT  
- **SPDX ID:** MIT  
- **Purpose:** HTTP client for GET/POST/PUT requests to FlightGear’s JSON property interface.

---

### **2.6 nlohmann/json**
- **Source:** FetchContent / single‑header include  
- **Repo:** [https://github.com/nlohmann/json](https://github.com/nlohmann/json)  
- **Version:** v3.x (header‑only)  
- **License:** MIT  
- **SPDX ID:** MIT  
- **Purpose:** JSON parsing and serialization.

---

### **2.7 Meson**
- **Source:** pip (`pip install meson`)  
- **Version:** pip‑resolved  
- **License:** Apache‑2.0  
- **SPDX ID:** Apache-2.0  
- **Purpose:** Required for building libpsl when curl is built with SSL on macOS/Windows.

---

## **3. SPDX Section**

```
SPDXVersion: SPDX-2.3
DataLicense: CC0-1.0
DocumentName: FlightgearMidi-SBOM
DocumentNamespace: https://github.com/shemeshg/FlightgearMidi/sbom

##### Packages #####

PackageName: libremidi
SPDXID: SPDXRef-libremidi
PackageVersion: master
PackageDownloadLocation: https://github.com/celtera/libremidi
PackageLicenseDeclared: MIT

PackageName: sigslot
SPDXID: SPDXRef-sigslot
PackageVersion: master
PackageDownloadLocation: https://github.com/palacaze/sigslot
PackageLicenseDeclared: MIT

PackageName: pybind11
SPDXID: SPDXRef-pybind11
PackageVersion: v2.12.0
PackageDownloadLocation: https://github.com/pybind/pybind11
PackageLicenseDeclared: BSD-3-Clause

PackageName: scikit-build-core
SPDXID: SPDXRef-scikit-build-core
PackageVersion: (pip-resolved)
PackageDownloadLocation: https://pypi.org/project/scikit-build-core/
PackageLicenseDeclared: MIT

PackageName: cpr
SPDXID: SPDXRef-cpr
PackageVersion: master
PackageDownloadLocation: https://github.com/libcpr/cpr
PackageLicenseDeclared: MIT

PackageName: nlohmann-json
SPDXID: SPDXRef-nlohmann-json
PackageVersion: v3.x
PackageDownloadLocation: https://github.com/nlohmann/json
PackageLicenseDeclared: MIT

PackageName: meson
SPDXID: SPDXRef-meson
PackageVersion: (pip-resolved)
PackageDownloadLocation: https://mesonbuild.com
PackageLicenseDeclared: Apache-2.0
```

---

## **4. Dependency Graph**

```
FlightgearMidi
 ├── libremidi (MIT)
 ├── sigslot (MIT)
 ├── pybind11 (BSD-3-Clause)
 ├── scikit-build-core (MIT)
 ├── cpr (MIT)
 ├── nlohmann-json (MIT)
 └── meson (Apache-2.0)
```

