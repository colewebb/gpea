from os import chdir, listdir, remove, path
import datetime
from tools import csvWriter, timer, runner, config
import cv2 as cv
import numpy as np

class otsureka:
    """
    A main class for the Otsu-based GPEureka algorithm. Contains members as follows:
     - self.currentImage: 
    """
    def __init__(self):
        self.cfg = config(f="/home/pi/Documents/gpea/config.json").config
        chdir("/home/pi/pics")
        self.currentImage = None
        self.oldImage = None
        self.currentWhitePixels = 0
        self.oldWhitePixels = 0
        self.dailyRGR = 0
        self.hourlyRGR = 0
        self.writer = csvWriter()
        self.time = datetime.datetime.now()

    def capture(self):
        name = str(self.time.month) + "-" + str(self.time.day) + "-" + str(self.time.year) + " " + str(self.time.hour) + "_" + str(self.time.minute) + ".png"
        runner("raspistill -br 50 -o '" + name + "'")
        self.currentImage = cv.imread(name)

    def analyze(self):
        self.currentImage = cv.cvtColor(self.currentImage, cv.COLOR_BGR2GRAY)
        self.oldImage = cv.cvtColor(self.oldImage, cv.COLOR_BGR2GRAY)
        self.currentImage = cv.threshold(self.currentImage, 0, 1, cv.THRESH_OTSU)[1]
        self.oldImage = cv.threshold(self.oldImage, 0, 1, cv.THRESH_OTSU)[1]
        self.currentWhitePixels = np.sum(self.currentImage == 1)
        self.oldWhitePixels = np.sum(self.oldImage == 1)
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
        runner("rclone copy ~/pics/ 'pi1:CPL Lab Group Folder/Cole/Pi5' -v")

    def main(self):
        old = datetime.datetime.now() - datetime.timedelta(days=1)
        self.oldImage = cv.imread(str(old.month) + "-" + str(old.day) + "-" + str(old.year) + " " + str(old.hour) + ":" + str(old.minute) + ".png")
        if self.oldImage is None:
            print("Exception")
            self.capture()
            self.backup()
            return
        else:
            self.capture()
            self.analyze()
            self.writer.write([self.time, self.currentWhitePixels, self.oldWhitePixels, self.pixelDelta, self.dailyRGR, self.hourlyRGR])
            self.cleanup()
            self.backup()

if __name__ == "__main__":
    otsureka = otsureka()
    otsureka.main()
