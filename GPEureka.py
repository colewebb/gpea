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
        name = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + ".png"
        os.system("raspistill -br 50 -o '" + name + "'")
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

    def cleanup(self):
        fileList = os.listdir("./")
        jpegs = []
        for f in fileList:
            if f.endswith(".jpg"):
                jpegs.append(f)
        if len(jpegs) >= 168:
            oldestFile = min(jpegs, key=os.path.getctime)
            os.remove(os.path.abspath(oldestFile))

    def logger(self, text, time):
        log = open("./" + time + ".log", 'a')
        log.write(text)
        log.close()

        
    def backup(self):
        os.system("rclone copy ~/pics/ 'pi1:CPL Lab Group Folder/Cole/Pi2' -v")

    def main(self):
        logTime = datetime.datetime.now()
        logTime = str(logTime.year) + str(logTime.month) + str(logTime.day) + str(logTime.hour) + str(logTime.minute)
        try:
            old = datetime.datetime.now() - datetime.timedelta(days=1)
            self.oldImage = Image.open(str(old.year) + str(old.month) + str(old.day) + str(old.hour) + str(old.minute) + ".png")
        except:
            self.capture()
            self.backup()
            return
        self.capture()
        self.analyze()
        self.writer.write([self.time, self.currentWhitePixels, self.oldWhitePixels, self.pixelDelta, self.dailyRGR, self.hourlyRGR])
        self.cleanup()
        self.backup()

if __name__ == "__main__":
    gpea = gpeureka()
    gpea.main()
