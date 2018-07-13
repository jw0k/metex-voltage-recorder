#!/usr/bin/python

import sys
import argparse
import serial
import random
import time

parser = argparse.ArgumentParser(description="Simulates Metex multimeter")
parser.add_argument("port", help="name of the COM port (e.g. COM7)")
args = parser.parse_args()

ser = serial.Serial()
ser.port = args.port
ser.baudrate = 1200
ser.bytesize = 7
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_TWO

ser.open()

count = 0

while True:
    buf = ser.read(1)
    if buf=="D":
        time.sleep(random.uniform(0.0, 0.3))
        if count%20 == 7:
            ser.write("AC  a240    V\r") #invalid message (14 bytes)
        elif count%20 == 15:
            ser.write("AC  0240 ") #invalid message (less than 14 bytes)
        elif count%20 == 19:
            ser.write("AC  0240    V\rsmieci") #invalid message (more than 14 bytes)
        else:
            v = random.uniform(230.0, 250.0)
            vs = "{:04.0f}".format(v)
            ser.write("AC  " + vs + "    V\r")
            
        count += 1

ser.close()
