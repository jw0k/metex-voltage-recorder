#!/usr/bin/python

import sys
import argparse
import serial
import time
import datetime

def stripCR(buf):
    result = buf.translate(None, "\r")
    return result

parser = argparse.ArgumentParser(description="Read serial input and write to standard output")
parser.add_argument("port", help="name of the COM port (e.g. COM7)")
parser.add_argument("-i", "--interval", type=int, default=10, help="interval between reads in seconds (10 by default)")
parser.add_argument("-b", "--baud", type=int, default=1200, help="baud rate (1200 by default)")
parser.add_argument("-s", "--bytesize", type=int, default=7, help="byte size in bits (7 by default)")
parser.add_argument("-p", "--parity", choices=["none", "even", "odd", "mark", "space"],
    default="none", help="the parity (none by default)")
parser.add_argument("-t", "--stopbits", choices=["one", "onepointfive", "two"],
    default="two", help="number of stopbits (two by default)")
args = parser.parse_args()

#this is a workaround to prevent sys.stdout.write from emitting CR when printing "\n"
if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

ser = serial.Serial()
ser.port = args.port
ser.baudrate = args.baud
ser.bytesize = args.bytesize
parityMap = {
    "none": serial.PARITY_NONE,
    "even": serial.PARITY_EVEN,
    "odd": serial.PARITY_ODD,
    "mark": serial.PARITY_MARK,
    "space": serial.PARITY_SPACE,
}
ser.parity = parityMap[args.parity]
stopbitsMap = {
    "one": serial.STOPBITS_ONE,
    "onepointfive": serial.STOPBITS_ONE_POINT_FIVE,
    "two": serial.STOPBITS_TWO,
}
ser.stopbits = stopbitsMap[args.stopbits]

ser.open()
sys.stderr.write(str(ser.in_waiting) + " bytes in buf after opening the port, flushing\n")
ser.reset_input_buffer()

while True:
    ser.write("D")
    buf = ser.read(14)
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    sys.stdout.write(timestamp+";"+buf+"\n")
    sys.stdout.flush()
    sys.stderr.write(timestamp + ";" + stripCR(buf) + " (" + str(ser.in_waiting) + " bytes remaining)\n");
    sys.stderr.flush()
    time.sleep(args.interval)

ser.close()
