import os
from PIL import Image
import numpy
import datetime
import RPi.GPIO as gp
from time import sleep

class csvWriter():
    def __init__(self):
        self.path = "./data.csv"
        if not os.path.exists(self.path):
            f = self.fileHandle()
            self.write(["Filename", "total interesting pixels", "fraction of total pixels", "analysis method"])
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
		
		
class switcher():
	def __init__(self):
		gp.setwarnings(False)
		gp.setmode(gp.BOARD)
		relevant_pins = [7, 11, 12, 15, 16, 21, 22]
		for pin in relevant_pins:
			gp.setup(pin, gp.OUT)
			gp.output(pin, True)
		self.switch_to(0)
		self.active = 0
	
	# assumes a zero offset (i.e., camera A is number 0)
	def switch_to(self, camera):
		offset = 4
		i2c = offset + camera
		os.system("i2cset -y 1 0x70 0x00 0x0" + str(i2c))
		if i2c == 4:
			gp.output(7, False)
			gp.output(11, False)
			gp.output(12, True)
			self.active = 0
		elif i2c == 5:
			gp.output(7, True)
			gp.output(11, False)
			gp.output(12, True)
			self.active = 1
		elif i2c == 6:
			gp.output(7, False)
			gp.output(11, True)
			gp.output(12, False)
			self.active = 2
		elif i2c == 7:
			gp.output(7, True)
			gp.output(11, True)
			gp.output(12, False)
			self.active = 3
		else:
			print("ERROR")
			
			
class ir_flash():
	def __init__(self):
		gp.setmode(gp.BOARD)
		gp.setup(36, gp.OUT)
		self.status = "off"
	
	def on(self):
		gp.output(36, True)
		self.status = "on"
	
	def off(self):
		gp.output(36, False)
		self.status = "off"
		
	def switch(self):
		if self.status == "on":
			self.off()
		if self.status == "off":
			self.on()
			
	def fire(self):
		self.on()
		sleep(60)
		self.off()
		

class camera():
	def __init__(self, ir, location, sw):
		self.ir = ir
		self.location = location
		self.sw = sw
		
	def takePicture(self):
		self.sw.switch_to(self.location)
		command = "raspistill -o '" + str(datetime.datetime.now()) + "'.png"
		os.system(command)

class imageAnalyzer:
	def __init__(self, imagePath):
		self.timer = timer()
		self.timer.startTimer()
		self.csv = csvWriter()
		self.imagePath = imagePath
		self.cleanImage = Image.open(imagePath)
		self.interestingPixelCount = 0
		self.size = self.cleanImage.size
		self.pixelCount = self.size[0] * self.size[1]
		self.name = "genericImageAnalyzer"
		
	def isInteresting(self, pixel):
		raise NotImplementedError
		
	def exportOutput(self):
		fraction = float(self.interestingPixelCount)/self.pixelCount
		print(self.imagePath + ", " + str(self.interestingPixelCount) + ", " + str(fraction) + ", " + self.name)
		self.csv.write([self.imagePath, self.interestingPixelCount, fraction, self.name])
		self.timer.endTimer()


class infraredThresholdBW(imageAnalyzer):
    def __init__(self, imagePath, threshold=175):
        imageAnalyzer.__init__(self, imagePath)
        self.name = "infraredThresholdBW"
        self.threshold = threshold
        self.analyzedImage = Image.open(imagePath).convert("L").point(self.calculateThreshold)
        self.analyzedImage.save("/home/pi/ANALYZED.png")
        self.im = numpy.array(self.analyzedImage)
    
    def calculateThreshold(self, i):
        if i > self.threshold:
            return 255
        else:
            return 0

    def isInteresting(self, pixel):
        if pixel == 255:
            self.interestingPixelCount += 1
            return True
        else:
            return False

    def main(self):
        for i in self.im:
            for j in i:
                self.isInteresting(j)
        self.exportOutput()
        
        
class infraredAdobeBW(imageAnalyzer):
	def __init__(self, imagePath, threshold=175):
		imageAnalyzer.__init__(self, imagePath)
		self.name = "infraredAdobeBW"
		self.threshold = threshold
		self.im = numpy.array(self.cleanImage)
		self.redBias = -40
		self.greenBias = 144
		self.blueBias = -3
		self.analyzeImage()
		print("image analyzed")
		Image.fromarray(self.im).save("/home/pi/adobe.png")
		
		
	def analyzeImage(self):
		for i in self.im:
			for j in i:
				j[0] += self.redBias
				j[1] += self.greenBias
				j[2] += self.blueBias
				for m in j:
					if m > 255:
						m = 255

	def isInteresting(self, pixel):
		if (int(pixel[0]) + int(pixel[1]) + int(pixel[2]))/3 > self.threshold:
			self.interestingPixelCount += 1
			
	def main(self):
		for i in self.im:
			for j in i:
				self.isInteresting(j)
		self.exportOutput()


def demo():
	s = switcher()
	color = camera(False, 0, s)
	ir = camera(True, 2, s)
	color.takePicture()
	ir.takePicture()
	
def shell():
	print("The shell isn't ready yet.")
	return
	s = switcher()
	cameras = []
	command = input("GPEA >>> ").lower()
	if command == "help":
		print(
"""Available commands:
     camera: creates a new camera
takePicture: takes a picture (it will ask which camera)
       help: display this message"""
		)
	elif command == "camera":
		ir = bool(input("Is this an IR camera? (True/False) >>> "))
		loc = int(input("Where is this camera on the switch? (0-3) >>> "))
		cameras.append(camera(ir, loc, s))
	
	
def main():
	while True:
		print(
"""WELCOME TO GPEA

Please select one of the following options:
1) Demo
2) Interactive Shell
3) Quit"""
		)
		choice = input(" >>> ")
		if choice == 1:
			demo()
		elif choice == 2:
			shell()
		elif choice == 3:
			exit(0)
		else:
			print("That is not a valid option")

if __name__ == "__main__":
	main()

