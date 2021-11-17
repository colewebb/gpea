import os, sys
import cv2 as cv
import numpy as np
import datetime
from re import split
from time import time

imageTypes = ["", ".jpg", ".png", ".tif"]


class analyzer():
    def __init__(self, imagePath) -> None:
        self.image = cv.imread(imagePath)

    def analyze(self) -> int:
        return 0

class otsu(analyzer):
    def analyze(self) -> int:
        if np.mean(self.image) < 20:
            return 0
        self.image = cv.cvtColor(self.image, cv.COLOR_RGB2GRAY)
        self.image = cv.threshold(self.image, 0, 1, cv.THRESH_OTSU)[1]
        interestingPixels = np.sum(self.image == 1)
        return interestingPixels

class hsvSegmentation(analyzer):
    def analyze(self) -> int:
        if np.mean(self.image) < 20:
            return 0
        self.image = cv.cvtColor(self.image, cv.COLOR_RGB2HSV)
        self.image = self.image[:, :, 0]
        min = 25
        max = 75
        # TODO: use cv threshold to optimize
        for i in range(0, len(self.image)):
            for j in range(0, len(self.image[0])):
                if self.image[i, j] > max or self.image[i, j] < min:
                    self.image[i, j] = 0
                else:
                    self.image[i, j] = 255
        interestingPixels = np.sum(self.image == 255)
        return interestingPixels


def pairwiseAnalyze(analysisType, imageType) -> None:
    startTime = time()
    f = open("./data.csv", 'w')
    f.write("OlderImage,NewerImage,OlderInterestingPixels,NewerInterestingPixels\n")
    f.flush()
    # TODO: add f.flush() after every write, save data in case of crash
    fileList = os.listdir("./")
    fileList = [f for f in fileList if f.endswith(imageTypes[imageType]) == True]
    imagePairs = 0
    print("Found " + str(len(fileList)) + " files. Analyzing...")
    for i in range(0, len(fileList)):
        olderImage = fileList[i]
        olderImage = split("-|\s|_", olderImage[:-4])
        oldTime = datetime.datetime(year=int(olderImage[2]), month=int(olderImage[0]), day=int(olderImage[1]), hour=int(olderImage[3]), minute=int(olderImage[4]))
        newTime = oldTime + datetime.timedelta(days=1)
        newerImage = str(newTime.month) + "-" + str(newTime.day) + "-" + str(newTime.year) + " " + str(newTime.hour) + "_" + str(newTime.minute) + imageTypes[imageType]
        olderImage = fileList[i]
        olderImageCV = cv.imread(olderImage)
        newerImageCV = cv.imread(newerImage)
        if olderImageCV is not None and newerImageCV is not None:
            imagePairs = imagePairs + 1
            if analysisType == 3:
                olderInterestingPixels = otsu(olderImage).analyze()
                newerInterestingPixels = otsu(newerImage).analyze()
            else:
                olderInterestingPixels = hsvSegmentation(olderImage).analyze()
                newerInterestingPixels = hsvSegmentation(newerImage).analyze()
            f.write(olderImage + "," + newerImage + "," + str(olderInterestingPixels) + "," + str(newerInterestingPixels) + "\n")
            f.flush()
            print("Image pair #" + str(imagePairs) + " analyzed")
    f.close()
    elapsedTime = time() - startTime
    print("Time elapsed: " + str(elapsedTime) + "s")


def analyze(analysisType, imageType) -> None:
    startTime = time()
    f = open("./data.csv", 'w')
    f.write("Filename,InterestingPixels\n")
    fileList = os.listdir("./")
    fileList = [f for f in fileList if f.endswith(imageTypes[imageType]) == True]
    print("Found " + str(len(fileList)) + " files. Analyzing...")
    for i in range(0, len(fileList)):
        if analysisType == 1:
            interestingPixels = otsu(fileList[i]).analyze()
        else:
            interestingPixels = hsvSegmentation(fileList[i]).analyze()
        f.write(str(fileList[i]) + "," + str(interestingPixels) + str("\n"))
        if i % 10 == 0 and i > 0:
            print(str(i) + " images done.")
    f.close()
    elapsedTime = time() - startTime
    print("Time elapsed: " + str(elapsedTime) + "s")

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
 - Enter 2 for HSV Segmentation
 - Enter 3 for Pairwise Otsu's Binarization
 - Enter 4 for Pairwise HSV Segmentation''')
    analysisType = input(" >>> ")
    try:
        analysisType = int(analysisType)
    except:
        print("Please enter a number. Exiting...")
        return
    if analysisType > 6 or analysisType < 1:
        print("Please enter a number between 1 and 6. Now exiting...")
        return
    print('''Enter file extension of images:
 - Enter 1 for .jpg
 - Enter 2 for .png
 - Enter 3 for .tif''')
    imageType = input(" >>> ")
    try:
        imageType = int(imageType)
    except:
        print("Please enter a number. Exiting...")
        return
    if imageType > 3 or imageType < 1:
        print("Please enter 1, 2, or 3. Now exiting...")
        return
    if analysisType > 2:
        pairwiseAnalyze(analysisType, imageType)
    else:
        analyze(analysisType, imageType)


if __name__ == "__main__":
    main()