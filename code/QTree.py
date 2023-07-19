import os
import shutil

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QTree(QTreeWidget):
    itemMoved = pyqtSignal()
    itemDropped = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.path = ""
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        self.itemMoved.emit()
        event.accept()
    
    def dropEvent(self, event):
        dropIndex = self.indexAt(event.pos())
        dropItem = self.itemFromIndex(dropIndex)
        
        selectedItem = self.selectedItems()[0]
        
        selectedPath = self.path+selectedItem.text(1)
        dropPath = self.path+dropItem.text(1)
                
        if '.' in dropPath:
            Lpath = dropPath.split('/')
            dropPath = '/'.join(Lpath[:-1])
        
        self.move(selectedPath, dropPath)
    
    def move(self, selectedPath, dropPath):
        newPath = os.path.join(dropPath, os.path.basename(selectedPath))
        
        if os.path.exists(newPath):
            return
        
        try:
            shutil.move(selectedPath, dropPath)
            self.itemDropped.emit()
        except:
            pass