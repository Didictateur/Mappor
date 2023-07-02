import os
import shutil

from .src import *

def importFolderTo(newFolderPath: str, currentFolderPath: str) -> None:
    """Makes a copy of the folder which the path in newFolderPath inside the folder wich the path is currentFolderPath

    Args:
        newFolderPath (str): the copied folder
        currentFolderPath (str): the folder in wich the new folder will be
    """
    folderName = newFolderPath.split('/')[-1]
    if folderName in os.listdir(currentFolderPath):
        raise Exception(f"The folder {folderName} already exists")
    os.mkdir(currentFolderPath+'/'+folderName)
    currentFolderPath += '/'+folderName
    
    def completeFolder(deepPath: str) -> None:
        for fileName in os.listdir(newFolderPath+'/'+deepPath):
            if os.path.isdir(newFolderPath+'/'+deepPath+fileName):
                os.mkdir(currentFolderPath+'/'+deepPath+fileName)
                completeFolder(deepPath+'/'+fileName)
            else:
                shutil.copy2(newFolderPath+deepPath+'/'+fileName, currentFolderPath+deepPath+'/'+fileName)
    
    completeFolder("")