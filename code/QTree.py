from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        event.accept()
    
    def dropEvent(self, event):
        print(event.mimeData().text())