import os, sys
import cv2 as cv
import numpy as np
import datetime
from re import split
from time import time
from tools import RGR, getInt

# TODO: Consider estimating remaining time during analysis
# TODO: Implement interpolation from analysis.ipynb or tools.py

imageTypes = ["", ".jpg", ".png", ".tif"]
analysisTypes = {"OTSU": 1,
    "OTSU_CC": 2,
    "HSV": 3,
    "OTSU_PAIRWISE": 4,
    "OTSU_CC_PAIRWISE": 5,
    "HSV_PAIRWISE": 6}

OTSU = 1
HSV = 2

def imageWrite(path, image):
    modPath = path.rsplit(".", 1)
    modPath = modPath[0] + "_ANALYZED." + modPath[1]
    cv.imwrite(modPath, image * 255)

class analyzer():
    def __init__(self, imagePath, ccc, morph, saveAnalyzed) -> None:
        self.imagePath = imagePath
        self.image = cv.imread(imagePath)
        self.ccc = ccc
        self.morph = morph
        self.saveAnalyzed = saveAnalyzed

    def analyze(self) -> int:
        return 0

class hsvSegmentation(analyzer):
    def analyze(self, bottom=35, top=50) -> int:
        if np.mean(self.image) < 20:
            return 0
        if bottom >= top:
            raise Exception("Bottom limit must be less than top limit")
        self.image = cv.cvtColor(self.image, cv.COLOR_RGB2HSV)
        self.image = self.image[:, :, 0]
        self.image = cv.inRange(self.image, bottom, top)/255
        self.image = self.image.astype(np.uint8)
        if self.ccc is True:
            (_, elementLabels, elementStats, _) = cv.connectedComponentsWithStats(self.image, 8)
            elementLabels = elementLabels[1:]
            elementStats = elementStats[1:]
            if len(elementStats) != 0:
                biggestElementLocation = np.where(elementStats[1:, 4] == max(elementStats[1:, 4]))[0][0] + 2
                elementLabels[elementLabels != biggestElementLocation] = 0
                self.image = elementLabels/biggestElementLocation
            else:
                self.ccc = False
        if self.morph is True:
            kernel = np.ones((10, 10), np.uint8)
            self.image = cv.dilate(cv.erode(self.image, kernel), kernel)
        if self.saveAnalyzed is True:
            if self.ccc is True:
                elementLabels[elementLabels != biggestElementLocation] = 0
                imageWrite(self.imagePath, elementLabels)
            else:
                imageWrite(self.imagePath, self.image)
        interestingPixels = np.sum(self.image != 0)
        return interestingPixels

class otsu(analyzer):
    def analyze(self) -> int:
        if np.mean(self.image) < 20:
            return 0
        self.image = cv.cvtColor(self.image, cv.COLOR_RGB2GRAY)
        self.image = cv.threshold(self.image, 0, 1, cv.THRESH_OTSU)[1]
        if self.ccc is True:
            (_, elementLabels, elementStats, _) = cv.connectedComponentsWithStats(self.image, 8)
            elementLabels = elementLabels[1:]
            elementStats = elementStats[1:]
            biggestElementLocation = np.where(elementStats[1:, 4] == max(elementStats[1:, 4]))[0][0] + 2
            interestingPixels = np.sum(elementLabels == biggestElementLocation)
            self.image = elementLabels/biggestElementLocation
        if self.morph is True:
            kernel = np.ones((10, 10), np.uint8)
            self.image = cv.dilate(cv.erode(self.image, kernel), kernel)
        if self.saveAnalyzed is True:
            if self.ccc is True:
                elementLabels[elementLabels != biggestElementLocation] = 0
                imageWrite(self.imagePath, elementLabels)
            else:
                imageWrite(self.imagePath, self.image)
        interestingPixels = np.sum(self.image == 1)
        return interestingPixels

def pairwiseAnalyze(analysisType, imageType, ccc, timeDelta, morph, saveAnalyzed, bottom, top) -> None:
    startTime = time()
    f = open("./data.csv", 'w')
    f.write("OlderImage,NewerImage,OlderInterestingPixels,NewerInterestingPixels,PixelDelta,DailyRGR\n")
    f.flush()
    fileList = os.listdir("./")
    fileList = [f for f in fileList if f.endswith(imageTypes[imageType]) == True]
    fileList = [f for f in fileList if f.endswith("ANALYZED." + imageTypes[imageType]) == False]
    fileList.sort(key=os.path.getctime)
    imagePairs = 0
    print("Found " + str(len(fileList)) + " files. Analyzing...")
    for i in range(0, len(fileList)):
        olderImage = fileList[i]
        olderImage = split("-|\s|_", olderImage[:-4])
        oldTime = datetime.datetime(year=int(olderImage[2]), month=int(olderImage[0]), day=int(olderImage[1]), hour=int(olderImage[3]), minute=int(olderImage[4]))
        newTime = oldTime + timeDelta
        newerImage = str(newTime.month) + "-" + str(newTime.day) + "-" + str(newTime.year) + " " + str(newTime.hour) + "_" + str(newTime.minute) + imageTypes[imageType]
        olderImage = fileList[i]
        olderImageCV = cv.imread(olderImage)
        newerImageCV = cv.imread(newerImage)
        if olderImageCV is not None and newerImageCV is not None:
            imagePairs = imagePairs + 1
            if analysisType == OTSU:
                olderInterestingPixels = otsu(olderImage, ccc, morph, saveAnalyzed).analyze()
                newerInterestingPixels = otsu(newerImage, ccc, morph, saveAnalyzed).analyze()
            elif analysisType == HSV and bottom is None and top is None:
                olderInterestingPixels = hsvSegmentation(olderImage, ccc, morph, saveAnalyzed).analyze()
                newerInterestingPixels = hsvSegmentation(newerImage, ccc, morph, saveAnalyzed).analyze()
            elif analysisType == HSV and bottom is not None and top is not None:
                olderInterestingPixels = hsvSegmentation(olderImage, ccc, morph, saveAnalyzed).analyze(bottom, top)
                newerInterestingPixels = hsvSegmentation(newerImage, ccc, morph, saveAnalyzed).analyze(bottom, top)
            else:
                print("That's not a valid option.")
                return
            f.write(olderImage + "," + newerImage + "," + str(olderInterestingPixels) + "," + str(newerInterestingPixels) + "," + str(newerInterestingPixels - olderInterestingPixels) + "," + str(RGR(olderInterestingPixels, newerInterestingPixels)) + "\n")
            f.flush()
            if i % 10 == 0 and i > 0:
                print(str(i) + " image pairs done.")
    f.close()
    elapsedTime = time() - startTime
    print("Time elapsed: " + str(elapsedTime)[0:6] + "s")


def analyze(analysisType, imageType, ccc, morph, saveAnalyzed, bottom, top) -> None:
    startTime = time()
    f = open("./data.csv", 'w')
    f.write("Filename,InterestingPixels\n")
    fileList = os.listdir("./")
    fileList = [f for f in fileList if f.endswith(imageTypes[imageType]) == True]
    fileList = [f for f in fileList if f.endswith("ANALYZED." + imageTypes[imageType]) == False]
    fileList.sort(key=os.path.getctime)
    print("Found " + str(len(fileList)) + " files. Analyzing...")
    for i in range(0, len(fileList)):
        if analysisType == OTSU:
            interestingPixels = otsu(fileList[i], ccc, morph, saveAnalyzed).analyze()
        elif analysisType == HSV and bottom is None and top is None:
            interestingPixels = hsvSegmentation(fileList[i], ccc, morph, saveAnalyzed).analyze()
        elif analysisType == HSV and bottom is not None and top is not None:
            interestingPixels = hsvSegmentation(fileList[i], ccc, morph, saveAnalyzed).analyze(bottom, top)
        else:
            print("That's not a valid option.")
            return
        f.write(str(fileList[i]) + "," + str(interestingPixels) + str("\n"))
        if i % 10 == 0 and i > 0:
            print(str(i) + " images done.")
    f.close()
    elapsedTime = time() - startTime
    print(str(i) + " images analyzed.")
    print("Time elapsed: " + str(elapsedTime)[0:6] + "s")

def main() -> None:
    print("Welcome to Cole's Magic Batch Analyzer!")
    print("What directory would you like to search in?")
    searchPath = input(" >>> ")
    try:
        os.chdir(searchPath)
    except:
        print("That path does not exist. Exiting...")
        return
    print('''What type of analysis is wanted? 
 - Enter 1 for Otsu's Binarization
 - Enter 2 for HSV Segmentation''')
    analysisType = getInt(lowerLimit=1, upperLimit=2)
    print('''Is connected component cleanup wanted?
 - Enter 1 for yes
 - Enter 0 for no''')
    ccc = bool(getInt())
    morph = False
    print('''Is morphological cleanup wanted?
 - Enter 1 for yes
 - Enter 0 for no''')
    morph = bool(getInt())
    print('''Is pairwise analysis wanted?
 - Enter 1 for yes
 - Enter 0 for no''')
    pairwise = bool(getInt())
    if pairwise is True:
        print("How many minutes (0-59) in the image delta?")
        minuteDelta = getInt(upperLimit=59)
        print("How many hours (0-23) in the image delta?")
        hourDelta = getInt(upperLimit=23)
        print("How many days (0-365) in the pixel delta?")
        dayDelta = getInt(upperLimit=365)
        timeDelta = datetime.timedelta(minutes=minuteDelta, hours=hourDelta, days=dayDelta)
    print('''Enter file extension of images:
 - Enter 1 for .jpg
 - Enter 2 for .png
 - Enter 3 for .tif''')
    imageType = getInt(lowerLimit=1, upperLimit=3)
    saveAnalyzed = False
    print('''Is analyzed image saving wanted?
 - Enter 1 for yes
 - Enter 0 for no''')
    saveAnalyzed = bool(getInt())
    bottom = None
    top = None
    if analysisType == 2:
        print('''Do you want to provide custom boundaries for the HSV segmentation?
 - Enter 1 for yes
 - Enter 0 for no''')
        customLimits = bool(getInt())
        if customLimits:
            print("Enter bottom limit (0-178):")
            bottom = getInt(upperLimit=178)
            print("Enter top limit:")
            top = getInt(lowerLimit=bottom, upperLimit=179)
    if pairwise:
        pairwiseAnalyze(analysisType, imageType, ccc, timeDelta, morph, saveAnalyzed, bottom, top)
    else:
        analyze(analysisType, imageType, ccc, morph, saveAnalyzed, bottom, top)


if __name__ == "__main__":
    main()