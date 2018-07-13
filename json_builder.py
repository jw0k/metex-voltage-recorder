#!/usr/bin/python

import sys
import argparse
import time
import datetime
import json

beginning = datetime.datetime.utcfromtimestamp(0)
def unix_time_millis(dt):
    return (dt - beginning).total_seconds() * 1000.0

parser = argparse.ArgumentParser(description="Read serial input and write to standard output")
parser.add_argument("inputPath", help="path to the input data.csv")
parser.add_argument("outputPath", help="path to the output voltages.json")
args = parser.parse_args()

#this is a workaround to prevent sys.stdout.write from emitting CR when printing "\n"
if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

time.sleep(11)

while True:
    with open(args.inputPath, "r") as d:
        lines = d.read().splitlines()
        if len(lines) > 6*60*24:
            lines = lines[-6*60*24:]

        data = [line.split(";") for line in lines]
        voltages = [int(item[1]) for item in data]
        minVoltage = min(voltages)
        maxVoltage = max(voltages)
        currVoltage = voltages[-1]

        data = data[0::6] # decimate data. after this, entries' interval should be 1 minute
        timestamps = [item[0] for item in data]
        voltages = [int(item[1]) for item in data]

        epochs = [int(unix_time_millis(datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")))
            for timestamp in timestamps]

        jsonObj = {}
        jsonObj["currentVoltage"] = currVoltage
        jsonObj["maxVoltage"] = maxVoltage
        jsonObj["minVoltage"] = minVoltage
        jsonObj["voltage"] = [{"x": epoch, "y": voltage} for epoch, voltage in zip(epochs, voltages)]

        with open(args.outputPath, "w") as f:
            json.dump(jsonObj, f)

        time.sleep(10)