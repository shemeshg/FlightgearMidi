from dataclasses import dataclass, field
from jinja2 import Environment, FileSystemLoader


# ---------------------------------------------------------
# Global Bindings
# ---------------------------------------------------------

@dataclass
class ByBindGlobal:
    opaque_item_types: list[str] = field(default_factory=list)


# ---------------------------------------------------------
# Data Models
# ---------------------------------------------------------

@dataclass
class OpaqueVector:
    vector_type: str
    py_name: str


@dataclass
class PyEnumClass:
    name: str
    elements: list[str]


@dataclass
class PyDefCallback:
    name: str
    signature: str


@dataclass
class PyClass:
    name: str
    defs: list[str] = field(default_factory=list)
    defs_pointer: list[str] = field(default_factory=list)
    defs_rw: list[str] = field(default_factory=list)
    defs_callback: list[PyDefCallback] = field(default_factory=list)
    has_constructor: bool = False
    is_shared_pointer: bool = False


# ---------------------------------------------------------
# Module Definition
# ---------------------------------------------------------

@dataclass
class PyBindModule:
    module_name: str
    global_bindings: ByBindGlobal
    opaque_vectors: list[OpaqueVector] = field(default_factory=list)
    defs: list[str] = field(default_factory=list)
    enums: list[PyEnumClass] = field(default_factory=list)
    classes: list[PyClass] = field(default_factory=list)

    def add_opaque_vector(self, vector_type: str, py_name: str):
        self.opaque_vectors.append(OpaqueVector(vector_type, py_name))
        self.global_bindings.opaque_item_types.append(vector_type)

    def add_def(self, ref_name: str):
        self.defs.append(ref_name)

    def add_enum(self, name: str, elements: list[str]):
        self.enums.append(PyEnumClass(name, elements))

    def add_class(self, cls: PyClass):
        self.classes.append(cls)


# ---------------------------------------------------------
# Jinja Environment
# ---------------------------------------------------------

environment = Environment(loader=FileSystemLoader("."))
template = environment.get_template("FlightgearMidiCog.j2")


# ---------------------------------------------------------
# Build Module
# ---------------------------------------------------------

g = ByBindGlobal()
m = PyBindModule("FlightgearMidi", g)

# Opaque vectors
m.add_opaque_vector("std::vector<DataConfigMidiInput>", "DataConfigMidiInputList")
m.add_opaque_vector("std::vector<DataConfigPullerFgKey>", "DataConfigPullerFgKeyList")
m.add_opaque_vector("std::vector<std::shared_ptr<DataConfigFromMidiToTelnet>>",
                    "DataConfigFromMidiToTelnetList")

# Module defs
m.add_def("getMidiClientItf")

# Enums
m.add_enum("MidiMsgType", ["CONTROL_CHANGE", "NOTE_ON", "NOTE_OFF"])

# Classes
m.add_class(PyClass(
    name="TelnetClient",
    has_constructor=True,
    defs=["openSocket", "getCmd", "stop"],
    defs_rw = ["telnetInitCmds"]
))

m.add_class(PyClass(
    name="LibreMidiOutPort",
    defs=["sendNoteOn", "sendNoteOff", "sendControlChange"]
))

m.add_class(PyClass(
    name="MidiClientItf",
    is_shared_pointer=True,
    defs=[
        "getDataConfig", "setDataConfig", "startMidiClient", "getIsTelnetRunning",
        "getInPorts", "getOutPorts", "setIsTerminalDebugMode", "sendTerminalRaw",
        "getIsTelnetDisconnectedSignal", "openLibreMidiOutPort"
    ],
    defs_pointer=["getLibreMidiOutPort"],
    defs_rw=["pullerSleepInterval"]
))

m.add_class(PyClass(
    name="DataConfigFromMidiToTelnet",
    has_constructor=True,
    is_shared_pointer=True,
    defs_rw=[
        "fromStart", "fromEnd", "toStart", "toEnd",
        "midiMsgType", "midiChannel", "notePitchOrCcChannel",
        "setCmd", "isCallback"
    ],
    defs_callback=[PyDefCallback("callback", "void(std::vector<int>)")]
))

m.add_class(PyClass(
    name="DataConfigMidiInput",
    has_constructor=True,
    defs_rw=["midiInputIdx", "midiInputName", "dataConfigFromMidiToTelnets"]
))

m.add_class(PyClass(
    name="DataConfigPullerFgKey",
    has_constructor=True,
    defs_rw=["fgKetPath"],
    defs_callback=[PyDefCallback("callback", "void(std::string, std::string)")]
))

m.add_class(PyClass(
    name="DataConfig",
    has_constructor=True,
    defs_rw=["telnetHost", "telnetPort","httpdPort","dataConfigMidiInputs", "dataConfigPullerFgKeys","telnetInitCmds"]
))


# ---------------------------------------------------------
# Render Output
# ---------------------------------------------------------

content = template.render(m=m)

def getText():
    return content

