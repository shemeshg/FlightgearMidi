import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(script_dir, "..", "build", "MyLibPy")

#sys.path.append("../build/MyLibPy")
sys.path.append(module_dir)

import MyLibPy

midi = MyLibPy.getMidiClientItf()
midi.testMidi()

line = input("Press Enter to continue...")

