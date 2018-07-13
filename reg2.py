#!/usr/bin/python

import sys
import argparse
import serial
import time
import datetime
import re

def writeToLog(d, log):
    d.write(log)
    d.flush()
    sys.stdout.write(log)
    sys.stdout.flush()

correct_metex_message = re.compile("^AC  \\d\\d\\d\\d    V\r$")
    
def correct(buf):
    return correct_metex_message.match(buf)

parser = argparse.ArgumentParser(description="Read serial input and write to standard output")
parser.add_argument("port", help="name of the COM port (e.g. COM7)")
parser.add_argument("outputPath", help="path to the output data.csv")
parser.add_argument("debugOutputPath", help="path to the debug log file")
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
d = open(args.debugOutputPath, "ab")
f = open(args.outputPath, "ab") #ab - append, binary
writeToLog(d, "{} bytes in buf after opening the port, flushing\n".format(ser.in_waiting))
ser.reset_input_buffer()

faultyReads = 0

while True:
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")

    ser.write("D")
    time.sleep(1)

    if ser.in_waiting != 14:
        faultyReads += 1
        log = "{}: faulty read - wrong number of bytes! ({} faulty reads in total); {} bytes in the buffer " \
            "(expected 14): {}\n".format(timestamp, faultyReads, ser.in_waiting, ser.read(ser.in_waiting))
        writeToLog(d, log)
        ser.reset_input_buffer()
        time.sleep(args.interval-1)
        continue

    buf = ser.read(14)
    if not correct(buf):
        faultyReads += 1
        log = "{}: faulty read - bad format! ({} faulty reads in total); contents: {}\n".format(
            timestamp, faultyReads, buf)
        writeToLog(d, log)
        ser.reset_input_buffer()
        time.sleep(args.interval-1)
        continue

    voltage = str(int(buf[3:3+6]))

    f.write("{};{}\n".format(timestamp, voltage))
    f.flush()

    log = "{}: {}\n".format(timestamp, buf)
    writeToLog(d, log)

    time.sleep(args.interval-1)

ser.close()
d.close()
f.close()
