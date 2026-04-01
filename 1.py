import serial
import time

# CHANGE THIS to your Arduino port:
PORT = "COM10"

BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)  # open port[web:42]
time.sleep(2)  # wait for Arduino reset

def fire_pulse():
  ser.write(b't')
  ser.flush()
  print("Pulse command sent")

def buzz():
  ser.write(b'b')
  ser.flush()
  print("Buzz command sent")

if __name__ == "__main__":
  while True:
    cmd = input("q to quit: ")
    if cmd.lower() == "ta": fire_pulse()
    elif cmd.lower() == "bu": buzz()
    elif cmd.lower() == "q": break
    else: print("INVALID!")

ser.close()