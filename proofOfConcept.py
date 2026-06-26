# pip install python-rtmidi mido flightgear_python

import threading
import time
import mido
from flightgear_python.fg_if import PropsConnection

# Connect to FlightGear
props_conn = PropsConnection('localhost', 5500)
props_conn.connect()

# Shared state
latest_values = {
    "throttle": 0.0,
    "mixture": 0.0,
    "rudder": 0.0,
    "aileron": 0.0,
    "elevator": 0.0
}
lock = threading.Lock()

# Worker thread: sends updates at fixed rate (e.g. 30 Hz)
def flightgear_sender():
    last_throttle = None
    last_mixture = None
    last_rudder = None
    last_aileron = None
    last_elevator = None

    while True:
        time.sleep(1/30)  # 30 updates per second

        with lock:
            throttle = latest_values["throttle"]
            mixture = latest_values["mixture"]
            rudder = latest_values["rudder"]
            aileron = latest_values["aileron"]
            elevator = latest_values["elevator"]


        # Send only the latest value
        if last_throttle is None or abs(throttle - last_throttle) > 0.009:            
            props_conn.set_prop('/controls/engines/engine/throttle', throttle)
            last_throttle = throttle

        if last_mixture is None or abs(mixture - last_mixture) > 0.009:
            step = 0.05
            quantized = round(mixture / step) * step
            # props_conn.set_prop('/controls/engines/engine/mixture', quantized)git init
            last_mixture =  mixture    
            print(quantized)   

        if last_rudder is None or abs(rudder - last_rudder) > 0.009:             
            props_conn.set_prop('/controls/flight/rudder', rudder)
            last_rudder = rudder        

        if last_aileron is None or abs(aileron - last_aileron) > 0.009:           
            props_conn.set_prop('/controls/flight/aileron', aileron)
            last_aileron = aileron                      

        if last_elevator is None or abs(elevator - last_elevator) > 0.009:            
            props_conn.set_prop('/controls/flight/elevator', elevator)
            last_elevator = aileron    

# Start worker thread
threading.Thread(target=flightgear_sender, daemon=True).start()

# MIDI input
print("Available MIDI input ports:")
ports = mido.get_input_names()
for i, p in enumerate(ports):
    print(f"{i}: {p}")

choice = int(input("Select MIDI port: "))
inport = mido.open_input(ports[choice])

print("Listening for MIDI...")

for msg in inport:
    if msg.type == 'control_change' and msg.control == 77:
        value = msg.value / 127.0

        # Update shared state without blocking
        with lock:
            latest_values["throttle"] = value

    #if msg.type == 'control_change' and msg.control == 78:
    #    value = msg.value / 127.0
    #
    #    # Update shared state without blocking
    #    with lock:
    #        latest_values["mixture"] = value

    if msg.type == 'control_change' and msg.control == 78:        
        value = (msg.value / 127.0) * 2 - 1  # convert 0–127 → -1 to +1
        with lock:
            latest_values["rudder"] = value * -1


    if msg.type == 'control_change' and msg.control == 79:        
        value = (msg.value / 127.0) * 2 - 1  # convert 0–127 → -1 to +1
        with lock:
            latest_values["aileron"] = value * -1

    if msg.type == 'control_change' and msg.control == 80:        
        value = (msg.value / 127.0) * 2 - 1  # convert 0–127 → -1 to +1
        with lock:
            latest_values["elevator"] = value


