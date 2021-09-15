from os import chdir, listdir, remove, path
import datetime
from .tools import csvWriter, timer, runner, config
import cv2 as cv
import numpy as np

class otsureka:
    """
    A main class for the Otsu-based GPEureka algorithm. Contains members as follows:
     - self.currentImage: 
    """
    def __init__(self):
        chdir("/home/pi/pics")
        self.currentImage = None
        self.oldImage = None
        self.currentWhitePixels = 0
        self.oldWhitePixels = 0
        self.dailyRGR = 0
        self.hourlyRGR = 0
        self.writer = csvWriter()
        self.time = datetime.datetime.now()
        self.cfg = config(f="/home/pi/Documents/gpea/config.json").config

    def capture(self):
        name = str(self.time.month) + "-" + str(self.time.day) + "-" + str(self.time.year) + " " + str(self.time.hour) + ":" + str(self.time.minute) + ".png"
        runner("raspistill -br 50 -o '" + name + "'")
        self.currentImage = cv.imread(name)

    def analyze(self):
        self.currentImage = self.currentImage[self.cfg["crop-left-x"]:self.cfg["crop-right-x"], self.cfg["crop-left-y"]:self.cfg["crop-right-y"]]
        self.oldImage = self.oldImage[self.cfg["crop-left-x"]:self.cfg["crop-right-x"], self.cfg["crop-left-y"]:self.cfg["crop-right-y"]]
        self.currentImage = cv.threshold(self.currentImage, 0, 1, cv.THRESH_OTSU)[1]
        self.oldImage = cv.threshold(self.oldImage, 0, 1, cv.THRESH_OTSU)[1]
        for i in range(len(self.currentImage)):
            for j in range(len(self.currentImage[0])):
                if self.currentImage[i, j] == 1:
                    self.currentWhitePixels += 1
        for i in range(len(self.oldImage)):
            for j in range(len(self.oldImage[0])):
                if self.oldImage[i, j] == 1:
                    self.oldWhitePixels += 1
        self.pixelDelta = self.currentWhitePixels - self.oldWhitePixels
        self.dailyRGR = np.log(float(self.currentWhitePixels)/self.oldWhitePixels)
        self.hourlyRGR = np.log(float(self.currentWhitePixels)/self.oldWhitePixels)/24

    def cleanup(self):
        fileList = listdir("./")
        jpegs = []
        for f in fileList:
            if f.endswith(".jpg"):
                jpegs.append(f)
        if len(jpegs) >= 168:
            oldestFile = min(jpegs, key=path.getctime)
            remove(path.abspath(oldestFile))
    
    def logger(self, text, time):
        log = open("./" + time + ".log", 'a')
        log.write(text)
        log.close()

    def backup(self):
        self.runner("rclone copy ~/pics/ 'pi1:CPL Lab Group Folder/Cole/Pi2' -v")

    def main(self):
        try:
            old = datetime.datetime.now() - datetime.timedelta(days=1)
            self.oldImage = cv.imread(str(old.month) + "-" + str(old.day) + "-" + str(old.year) + " " + str(old.hour) + ":" + str(old.minute) + ".png")
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
    otsureka = otsureka()
    otsureka.main()
