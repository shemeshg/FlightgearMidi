# **SBOM.md**

## **Software Bill of Materials (SBOM)**  
Project: **FlightgearMidi**  
Repository: [https://github.com/shemeshg/FlightgearMidi](https://github.com/shemeshg/FlightgearMidi)  
Generated: 2026‑07‑10  
Format: SPDX‑lite (human‑readable)

---

## **1. Project Summary**

**FlightgearMidi** is a C++/Python module that bridges MIDI input to FlightGear’s telnet interface.  
It uses:

- A C++17 backend  
- Python bindings via **pybind11**  
- MIDI I/O via **libremidi**  
- Signal/slot dispatch via **sigslot**  
- Python packaging via **scikit‑build‑core**

Source structure (from repo):  
- `FlightgearMidi/` (C++ backend)  
- `MyLib/` (supporting C++ code)  
- `testPy/` (Python example)  
- `CMakeLists.txt` (build system)  
- `pyproject.toml` (Python build backend)  


---

## **2. Third‑Party Components**

### **2.1 libremidi**
- **Source:** FetchContent  
- **Repo:** [https://github.com/celtera/libremidi](https://github.com/celtera/libremidi)  
- **Version:** `master`  
- **License:** MIT  
- **SPDX ID:** `MIT`  
- **Purpose:** Cross‑platform MIDI input/output.

---

### **2.2 sigslot**
- **Source:** FetchContent  
- **Repo:** [https://github.com/palacaze/sigslot](https://github.com/palacaze/sigslot)  
- **Version:** `master`  
- **License:** MIT  
- **SPDX ID:** `MIT`  
- **Purpose:** Lightweight signal/slot mechanism.

---

### **2.3 pybind11**
- **Source:** FetchContent  
- **Repo:** [https://github.com/pybind/pybind11](https://github.com/pybind/pybind11)  
- **Version:** `v2.12.0`  
- **License:** BSD‑3‑Clause  
- **SPDX ID:** `BSD-3-Clause`  
- **Purpose:** Python bindings for C++.

---

### **2.4 scikit‑build‑core**
- **Source:** Python build backend (`pyproject.toml`)  
- **Version:** unspecified (pip‑resolved)  
- **License:** MIT  
- **SPDX ID:** `MIT`  
- **Purpose:** Modern Python build backend integrating CMake.

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
```

---

## **4. Dependency Graph**

```
FlightgearMidi
 ├── libremidi (MIT)
 ├── sigslot (MIT)
 ├── pybind11 (BSD-3-Clause)
 └── scikit-build-core (MIT)
```
