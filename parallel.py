from batch import otsu
import multiprocessing as mp
import os
import time

def parallelAnalyzer(imagePath, ccc, morph, saveAnalyzed):
    return otsu(imagePath, ccc, morph, saveAnalyzed).analyze()

if __name__ == "__main__":
    os.chdir("F:/Pi13")
    fileList = os.listdir("./")
    fileList = [f for f in fileList if f.endswith(".png") == True]
    fileList = [f for f in fileList if f.endswith("ANALYZED.png") == False]
    fileList.sort(key=os.path.getctime)
    
    pool = mp.Pool(mp.cpu_count())
    start = time.time()
    results = pool.starmap(parallelAnalyzer, [(path, True, False, True) for path in fileList])
    print(time.time() - start)
    pool.close()