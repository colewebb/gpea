from PIL import Image, ExifTags
from datetime import datetime
import os

os.chdir("C:/Users/Admin/Documents/scripts/gpea/Pictures")

img = Image.open("exif_test.jpg")
print(img.getexif())
date = str(img.getexif()[306])[:-3]
dateObject = datetime.strptime(date, '%Y:%m:%d %H:%M')
print(dateObject)
