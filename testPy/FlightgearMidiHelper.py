import os
import sys
import logging
import threading
import time
from dataclasses import dataclass
from typing import Any, Iterable, Tuple

# ---------------------------------------------------------------------------
# MODULE PATH SETUP
# ---------------------------------------------------------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(script_dir, "..", "build", "FlightgearMidi")
sys.path.append(module_dir)

import FlightgearMidi
print("Loaded module from:", FlightgearMidi.__file__)

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

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

# ---------------------------------------------------------------------------
# TELNET WORKER
# ---------------------------------------------------------------------------

class TelnetWorkerManager:
    """Background worker that monitors and reconnects the Telnet interface."""

    def __init__(self, midiClientItf: FlightgearMidi.MidiClientItf):
        self.midi = midiClientItf
        self.thread: threading.Thread | None = None
        self.stop_flag = False
        self.max_attempts = 5
        self.attempts = 0

    def worker(self) -> None:
        logger.info("Telnet worker started")
        self.attempts = 0

        while not self.stop_flag:
            time.sleep(2)

            try:
                running = self.midi.getIsTelnetRunning()
                disconnected = self.midi.getIsTelnetDisconnectedSignal()

                if running:
                    self.attempts = 0
                    continue

                # Need reconnect
                if self.attempts >= self.max_attempts:
                    logger.error("Max reconnect attempts reached. Waiting for manual restart.")
                    break

                self.attempts += 1
                logger.warning(f"Reconnect attempt {self.attempts}/{self.max_attempts}...")

                ok = self.midi.startMidiClient()
                logger.info(f"Reconnect result: {ok}")

                if ok:
                    self.attempts = 0

            except Exception as e:
                logger.error(f"Telnet worker error: {e}")

        logger.info("Telnet worker stopped")

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            logger.info("Telnet worker already running")
            return

        self.stop_flag = False
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()
        logger.info("Telnet worker started")

    def stop(self) -> None:
        if self.thread and self.thread.is_alive():
            logger.info("Stopping Telnet worker...")
            self.stop_flag = True
            self.thread.join(timeout=2)
            logger.info("Telnet worker stopped")

    def restart(self) -> None:
        logger.info("Restarting Telnet worker...")
        self.stop()
        self.start()

# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

def main_loop(midi: FlightgearMidi.MidiClientItf) -> None:
    """Interactive console loop with automatic Telnet monitoring."""

    worker_mgr = TelnetWorkerManager(midi)
    worker_mgr.start()

    terminal_mode = False

    try:
        if not midi.startMidiClient():
            logger.error("Failed to start MIDI client.")
            sys.exit(1)

        while True:
            if midi.getIsTelnetRunning():
                user_input = input()

                if not terminal_mode:
                    logger.info("Connected\nq=quit\nt=toggle terminal mode")

                if user_input == "q":
                    break
                elif user_input == "t":
                    terminal_mode = not terminal_mode
                    midi.setIsTerminalDebugMode(terminal_mode)
                    if terminal_mode:
                        logger.info("Terminal mode enabled.")
                elif terminal_mode:
                    midi.sendTerminalRaw(user_input)

            else:
                logger.info("Not Connected\n r=restart q=quit")
                user_input = input()

                if user_input == "q":
                    break
                elif user_input == "r":
                    worker_mgr.restart()

    except Exception as e:
        logger.exception("Unhandled exception: %s", e)

    finally:
        worker_mgr.stop()


if __name__ == "__main__":
    exit(0)
