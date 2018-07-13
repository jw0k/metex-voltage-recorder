#!/usr/bin/python

import sys

#this is a workaround to prevent sys.stdout.write from emitting CR when printing "\n"
if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

while True:
    line = sys.stdin.readline()[:-1]
    data = line.split(";")
    voltage = float(data[1][3:3+6])
    sys.stdout.write(data[0] + ";" + str(voltage) + "\n")
    sys.stdout.flush()