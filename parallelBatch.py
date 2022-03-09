from batch import otsu
from tools import getInt
import os
import multiprocessing as mp
import time

def parallelAnalyzer(imagePath, ccc, morph, saveAnalyzed):
    return otsu(imagePath, ccc, morph, saveAnalyzed).analyze()

def main() -> None:
    imageTypes = ["", ".jpg", ".png", ".tif"]

    print("Welcome to Cole's Magic Batch Analyzer, now with ∞% more parallelization!")
    print("What directory would you like to search in?")
    searchPath = input(" >>> ")
    try:
        os.chdir(searchPath)
    except:
        print("That path does not exist. Exiting...")
        return
    print('''Is connected component cleanup wanted?
 - Enter 1 for yes
 - Enter 0 for no''')
    ccc = bool(getInt())
    morph = False
    print('''Is morphological cleanup wanted?
 - Enter 1 for yes
 - Enter 0 for no''')
    morph = bool(getInt())
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
    print("Analyzing, please wait...")

    fileList = os.listdir("./")
    fileList = [f for f in fileList if f.endswith(imageTypes[imageType]) == True]
    fileList = [f for f in fileList if f.endswith("ANALYZED" + imageTypes[imageType]) == False]
    fileList.sort(key=os.path.getctime)
    
    f = open("./data.csv", 'w')
    f.write("Filename,InterestingPixels\n")

    pool = mp.Pool(mp.cpu_count())
    start = time.time()
    results = pool.starmap(parallelAnalyzer, [(path, ccc, morph, saveAnalyzed) for path in fileList])
    print(str(time.time() - start)[:7] + "s, " + str(len(fileList)) + " images analyzed\nWriting CSV")
    pool.close()

    for i in range(0, len(fileList)):
        f.write(str(fileList[i]) + "," + str(results[i]) + "\n")
        f.flush()
    
    f.close()
    
if __name__ == "__main__":
    main()