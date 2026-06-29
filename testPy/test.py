import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(script_dir, "..", "build", "MyLibPy")

#sys.path.append("../build/MyLibPy")
sys.path.append(module_dir)

import MyLibPy


midi = MyLibPy.getMidiClientItf()

print("in ports:\n" + "\n".join(" " + p for p in midi.getInPorts()))
print("out ports:\n" + "\n".join(" " + p for p in midi.getOutPorts()))
print()

terminal_mode = False

try:
    midi.startMidiClient()

    while True:
        if midi.getIsTelnetRunning():
            user_input = input()

            if terminal_mode:
                # In terminal mode, only raw commands are sent
                pass
            else:
                print("\nConnected\nq=quit\nt=terminal mode on/off")

            if user_input == "q":
                break

            elif user_input == "t":
                terminal_mode = not terminal_mode
                midi.setIsTerminalDebugMode(terminal_mode)

                if terminal_mode:
                    print("t - to exit terminal mode")

            elif terminal_mode:
                midi.sendTerminalRaw(user_input)

        else:
            # Not connected
            if midi.getIsTelnetDisconnectedSignal():
                print("Try to Restart")
                midi.startMidiClient()
            else:
                print("Not Connected\n r=restart q=quit")
                user_input = input()

                if user_input == "q":
                    break
                elif user_input == "r":
                    midi.startMidiClient()

except Exception as e:
    print(e)


