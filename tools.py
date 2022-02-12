import os
import datetime
import subprocess
import json
import numpy as np
from sys import exit
import pandas as pd

class csvWriter():
    def __init__(self):
        self.path = "./data.csv"
        if not os.path.exists(self.path):
            f = self.fileHandle()
            self.write(["Timestamp", "Current White Pixels", "Old White Pixels", "Pixel Count Delta", "Daily RGR", "Hourly RGR"])
            f.close()

    def fileHandle(self):
        return open(self.path, "a")

    def format(self, data):
        toReturn = ""
        for i in data:
            toReturn += (str(i) + ",")
        return toReturn[:-1]
    
    def write(self, data):
        f = self.fileHandle()
        f.write(self.format(data) + "\n")
        f.close()


class timer():
	def __init__(self):
		self.startTime = None
		
	def startTimer(self):
		self.startTime = datetime.datetime.now()
		
	def endTimer(self):
		elapsedTime = datetime.datetime.now() - self.startTime()
		print(str(elapsedTime) + " time elapsed")
		return elapsedTime

class config():
    def __init__(self, f="./config.json"):
        self.config = json.load(open(f))

def runner(execute):
    return subprocess.run(execute, shell=True, capture_output=True, text=True)

def pixels2area(plantHeight, pixelCount, xResolution=3280, yResolution=2464):
    print("This number is for a growth chamber dimensioned 44cm X by 59cm Y.")
    conversionFactor = ((-174 * plantHeight) + 15416.268)/(xResolution * yResolution)
    return pixelCount * conversionFactor

def logger(text, time):
    log = open("./" + time + ".log", 'a')
    log.write(text)
    log.close()

def RGR(firstMeasurement, secondMeasurement, timeDelta=1):
    try:
        return float(np.log((secondMeasurement/firstMeasurement)/timeDelta))
    except ZeroDivisionError:
        return 0

def getInt(prompt=" >>> ", lowerLimit=0, upperLimit=1):
    number = input(prompt)
    try:
        number = int(number)
    except:
        print("That is not a number.")
        exit(1)
    if number > upperLimit or number < lowerLimit:
        print("That number is out of range.")
        exit(1)
    return number

def rollingAverage(n, data):
    return np.convolve(data, np.ones(n), 'valid')/n

def interpolate(data):
    """Returns a linearly interpolated 1D
    list of data, replacing any zeros with
    interpolated points.
    
    Will also interpolate NaN values.
    
    Takes a 1D list of values."""
    data = pd.DataFrame([f if f != 0 else None for f in data])
    data = data.interpolate()
    data = data.values.tolist()
    return [i[0] for i in data]