import os
import sys
import logging
import threading
import time
from dataclasses import dataclass
from typing import Optional, Any

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
# CONFIG CREATION
# ---------------------------------------------------------------------------

def add_mapping(midi_input, from_start, from_end, to_start, to_end, msg_type, channel, cc, cmd):
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






class TelnetWorkerManager:
    def __init__(self, midiClientItf: FlightgearMidi.MidiClientItf):
        self.thread = None
        self.stop_flag = False
        self.max_attempts = 5
        self.attempts = 0
        self.midiClientItf = midiClientItf

    def worker(self):
        """Background telnet monitor."""
        logger.info("Telnet worker started")
        self.attempts = 0  # reset attempts on start

        while not self.stop_flag:
            time.sleep(2)

            try:
                running = self.midiClientItf.getIsTelnetRunning()
                disconnected = self.midiClientItf.getIsTelnetDisconnectedSignal()

                # If already running, reset attempts counter
                if running:
                    self.attempts = 0
                    continue

                # If not running OR disconnected → attempt reconnect
                if not running or disconnected:
                    if self.attempts >= self.max_attempts:
                        logger.error("Max reconnect attempts reached (5). Giving up until manual restart.")
                        break

                    self.attempts += 1
                    logger.warning(f"Reconnect attempt {self.attempts}/5...")

                    ok = self.midiClientItf.startMidiClient()
                    logger.info(f"Reconnect result: {ok}")

                    # If reconnect succeeded → reset counter
                    if ok:
                        self.attempts = 0

                    continue

            except Exception as e:
                logger.error(f"Reconnect thread error: {e}")

        logger.info("Telnet worker stopped")

    def start(self):
        """Start worker if not running."""
        if self.thread and self.thread.is_alive():
            logger.info("Worker already running")
            return

        self.stop_flag = False
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()
        logger.info("Worker started")

    def stop(self):
        """Stop worker gracefully."""
        if self.thread and self.thread.is_alive():
            logger.info("Stopping worker...")
            self.stop_flag = True
            self.thread.join(timeout=2)
            logger.info("Worker stopped")

    def restart(self):
        """Restart worker cleanly."""
        logger.info("Restarting worker...")
        self.stop()
        self.start()





# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

def main_loop(midiClientItf: FlightgearMidi.MidiClientItf):


    # NEW CLEAN WORKER
    worker_mgr = TelnetWorkerManager(midiClientItf)
    worker_mgr.start()

    terminal_mode = False

    try:
        if not midiClientItf.startMidiClient():
            logger.error("Failed to start MIDI client.")
            sys.exit(1)

        while True:
            if midiClientItf.getIsTelnetRunning():
                user_input = input()

                if not terminal_mode:
                    logger.info("Connected\nq=quit\nt=toggle terminal mode")

                if user_input == "q":
                    break
                elif user_input == "t":
                    terminal_mode = not terminal_mode
                    midiClientItf.setIsTerminalDebugMode(terminal_mode)
                    if terminal_mode:
                        logger.info("Terminal mode enabled.")
                elif terminal_mode:
                    midiClientItf.sendTerminalRaw(user_input)

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
