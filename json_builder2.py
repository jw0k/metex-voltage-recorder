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

FILTER_WINDOW = 9 # must be odd (e.g. 3, 5, 7, etc.)

while True:
    with open(args.inputPath, "r") as d:
        lines = d.read().splitlines()

        data = [line.split(";") for line in lines]
        voltages = [int(item[1]) for item in data]
        timestamps = [item[0] for item in data]
        index, minVoltage = min(enumerate(voltages), key=lambda item:item[1])
        minVoltageTimestamp = timestamps[index]
        index, maxVoltage = max(enumerate(voltages), key=lambda item:item[1])
        maxVoltageTimestamp = timestamps[index]
        currVoltage = voltages[-1]
        currTimestamp = timestamps[-1]

        
        ########################## simple low-pass filter ##########################
        halfWindow = FILTER_WINDOW/2
        leftSentinel = [voltages[index+1] for index in reversed(range(halfWindow))]
        rightSentinel = [voltages[-2-index] for index in range(halfWindow)]
        voltagesWithSentinels = leftSentinel + voltages + rightSentinel + [0]
        vSum = sum(leftSentinel) + sum(voltages[0:halfWindow+1])
        lowPassVoltages = []

        for index in range(len(voltages)):
            lowPassVoltages.append(vSum/float(FILTER_WINDOW))
            vSum -= voltagesWithSentinels[index]
            vSum += voltagesWithSentinels[index+FILTER_WINDOW]
        #############################################################################

        
        
        timestamps = timestamps[0::6] # decimate data. after this, entries' interval should be 1 minute
        lowPassVoltages = lowPassVoltages[0::6]
        epochs = [int(unix_time_millis(datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")))
            for timestamp in timestamps]
        currEpoch = epochs[-1]

        DAY = 1000*60*60*24 # in ms
        revIndex = next((revIndex for revIndex, epoch in enumerate(reversed(epochs)) if currEpoch-epoch>=DAY), None)
        if revIndex:
            epochs = epochs[-revIndex-1:]
            lowPassVoltages = lowPassVoltages[-revIndex-1:]

        jsonObj = {}
        jsonObj["currentTimestamp"] = currTimestamp
        jsonObj["currentVoltage"] = currVoltage
        jsonObj["maxVoltageTimestamp"] = maxVoltageTimestamp
        jsonObj["minVoltageTimestamp"] = minVoltageTimestamp
        jsonObj["maxVoltage"] = maxVoltage
        jsonObj["minVoltage"] = minVoltage
        jsonObj["voltage"] = [{"x": epoch, "y": voltage} for epoch, voltage in zip(epochs, lowPassVoltages)]

        with open(args.outputPath, "w") as f:
            json.dump(jsonObj, f)

        time.sleep(10)
