import os
import datetime
from glob import iglob
from PIL import Image
import numpy as np

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
        os.chdir("/home/pi/pics")
        self.currentImage = None
        self.oldImage = None
        self.currentWhitePixels = 0
        self.oldWhitePixels = 0
        self.pixelDelta = 0
        self.dailyRGR = 0
        self.hourlyRGR = 0
        self.threshold = 110
        self.writer = csvWriter()
        self.timer = timer()
        self.time = datetime.datetime.now()

    def capture(self):
        now = datetime.datetime.now()
        name = str(now) + ".png"
        os.system("raspistill -o '" + name + "'")
        self.currentImage = Image.open(name)

    def analyze(self):
        self.currentImage = np.array(self.currentImage)
        self.oldImage = np.array(self.oldImage)
        for i in self.currentImage:
            for j in i:
                if (int(j[0]) + int(j[1]) + int(j[2]))/3 > self.threshold:
                    self.currentWhitePixels += 1
        for i in self.oldImage:
            for j in i:
                if (int(j[0]) + int(j[1]) + int(j[2]))/3 > self.threshold:
                    self.oldWhitePixels += 1
        self.pixelDelta = self.currentWhitePixels - self.oldWhitePixels
        self.dailyRGR = np.log(float(self.currentWhitePixels)/self.oldWhitePixels)
        self.hourlyRGR = np.log(float(self.currentWhitePixels)/self.oldWhitePixels)/24

    def main(self):
        try:
            self.oldImage = Image.open(max(iglob("/home/pi/pics/*.png"), key=os.path.getctime))
        except:
            self.capture()
            return
        self.capture()
        self.analyze()
        self.writer.write([self.time, self.currentWhitePixels, self.oldWhitePixels, self.pixelDelta, self.dailyRGR, self.hourlyRGR])

if __name__ == "__main__":
    gpea = gpeureka()
    gpea.main()

# TODO: remove old images
# TODO: upload files to box by rsync
# TODO: log timing
# TODO: set brightness
