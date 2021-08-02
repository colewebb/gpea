import os
import datetime

class csvWriter():
    def __init__(self):
        self.path = "./data.csv"
        if not os.path.exists(self.path):
            f = self.fileHandle()
            self.write(["Timestamp", "Current White Pixels", "Old White Pixels", "Pixel Count Delta", "RGR"])
            f.close()

    def fileHandle(self):
        return open(self.path, "a")

    def format(self, data):
        toReturn = ""
        for i in data:
            toReturn += (str(i) + ", ")
        return toReturn[:-2]
    
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

class gpeureka():
    def __init__(self):
         pass