from PyQt5.QtWidgets import * 
from PyQt5.QtCore import * 
from PyQt5.QtGui import *

import sys
from pathlib import Path

current_path = Path(__file__).parent.absolute()
root_path = current_path.parent.parent

class HelpWindow(QMainWindow):
   def __init__(self):
      super().__init__()
      self.setWindowTitle("Tutorial")
      self.initUI()

   def initUI(self):
      self.mainWindow = QWidget(self)
      self.mainWindow.setMinimumSize(580, 800)
      
      layout = QVBoxLayout(self.mainWindow)
      self.tab = QTabWidget(self)
      
      self.tabHierarchy = QWidget()
      self.tabMain = QWidget()
      self.tabTile = QWidget()
      self.tabDraw = QWidget()
      self.tabMap = QWidget()
      self.tabShort = QWidget()

      self.tab.addTab(self.tabHierarchy, "How a map is constitute")
      self.tab.addTab(self.tabMain, "Main window")
      self.tab.addTab(self.tabTile, "Tile")
      self.tab.addTab(self.tabDraw, "Draw")
      self.tab.addTab(self.tabMap, "Map")
      self.tab.addTab(self.tabShort, "Shortcuts")

      self.setupHierarchy()
      self.setupMainWindow()
      self.setupTile()
      self.setupDraw()
      self.setupMap()
      self.setupShort()

      layout.addWidget(self.tab)
      self.setCentralWidget(self.mainWindow)
      
   
   def setupHierarchy(self):
      layout = QVBoxLayout(self.tabHierarchy)
      scrollArea = QScrollArea()
      
      #Set scroll area
      contentWidget = QWidget()
      contentLayout = QVBoxLayout(contentWidget)
      scrollArea.setWidget(contentWidget)
      scrollArea.setWidgetResizable(True)
      
      #Body of the tab      
      img = QLabel()
      #pixmap = QPixmap(str(current_path)+"/img/helper/Hierarchy/Mappor.png")
      pixmap = QPixmap("./img/helper/Mappor.png")
      ratio = pixmap.size().height()/pixmap.size().width()
      newsize = 500
      pixmap = pixmap.scaled(newsize, int(newsize*ratio), Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
      img.setPixmap(pixmap)
      contentLayout.addWidget(img)
      
      #Finish scroll area
      layout.addWidget(scrollArea)
   
   def setupMainWindow(self):
      layout = QVBoxLayout(self.tabMain)
      scrollArea = QScrollArea()
      
      #Set scroll area
      contentWidget = QWidget()
      contentLayout = QVBoxLayout(contentWidget)
      scrollArea.setWidget(contentWidget)
      scrollArea.setWidgetResizable(True)
      
      #Body of the tab      
      img = QLabel()
      #pixmap = QPixmap(str(current_path)+"/img/helper/Hierarchy/Mappor.png")
      pixmap = QPixmap("./img/helper/MainWindow.png")
      ratio = pixmap.size().height()/pixmap.size().width()
      newsize = 500
      pixmap = pixmap.scaled(newsize, int(newsize*ratio), Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
      img.setPixmap(pixmap)
      contentLayout.addWidget(img)
      
      #Finish scroll area
      layout.addWidget(scrollArea)
   
   def setupTile(self):
      layout = QVBoxLayout(self.tabTile)
      scrollArea = QScrollArea()
      
      #Set scroll area
      contentWidget = QWidget()
      contentLayout = QVBoxLayout(contentWidget)
      scrollArea.setWidget(contentWidget)
      scrollArea.setWidgetResizable(True)
      
      #Body of the tab      
      img = QLabel()
      #pixmap = QPixmap(str(current_path)+"/img/helper/Hierarchy/Mappor.png")
      pixmap = QPixmap("./img/helper/TileMod.png")
      ratio = pixmap.size().height()/pixmap.size().width()
      newsize = 500
      pixmap = pixmap.scaled(newsize, int(newsize*ratio), Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
      img.setPixmap(pixmap)
      contentLayout.addWidget(img)
      
      #Finish scroll area
      layout.addWidget(scrollArea)
      
   def setupDraw(self):
      layout = QVBoxLayout(self.tabDraw)
      scrollArea = QScrollArea()
      
      #Set scroll area
      contentWidget = QWidget()
      contentLayout = QVBoxLayout(contentWidget)
      scrollArea.setWidget(contentWidget)
      scrollArea.setWidgetResizable(True)
      
      #Body of the tab      
      img = QLabel()
      #pixmap = QPixmap(str(current_path)+"/img/helper/Hierarchy/Mappor.png")
      pixmap = QPixmap("./img/helper/DrawMod.png")
      ratio = pixmap.size().height()/pixmap.size().width()
      newsize = 500
      pixmap = pixmap.scaled(newsize, int(newsize*ratio), Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
      img.setPixmap(pixmap)
      contentLayout.addWidget(img)
      
      #Finish scroll area
      layout.addWidget(scrollArea)
   
   def setupHierarchy(self):
      layout = QVBoxLayout(self.tabHierarchy)
      scrollArea = QScrollArea()
      
      #Set scroll area
      contentWidget = QWidget()
      contentLayout = QVBoxLayout(contentWidget)
      scrollArea.setWidget(contentWidget)
      scrollArea.setWidgetResizable(True)
      
      #Body of the tab      
      img = QLabel()
      #pixmap = QPixmap(str(current_path)+"/img/helper/Hierarchy/Mappor.png")
      pixmap = QPixmap("./img/helper/Mappor.png")
      ratio = pixmap.size().height()/pixmap.size().width()
      newsize = 500
      pixmap = pixmap.scaled(newsize, int(newsize*ratio), Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
      img.setPixmap(pixmap)
      contentLayout.addWidget(img)
      
      #Finish scroll area
      layout.addWidget(scrollArea)
      
   def setupMap(self):
      layout = QVBoxLayout(self.tabMap)
      scrollArea = QScrollArea()
      
      #Set scroll area
      contentWidget = QWidget()
      contentLayout = QVBoxLayout(contentWidget)
      scrollArea.setWidget(contentWidget)
      scrollArea.setWidgetResizable(True)
      
      #Body of the tab      
      img = QLabel()
      #pixmap = QPixmap(str(current_path)+"/img/helper/Hierarchy/Mappor.png")
      pixmap = QPixmap("./img/helper/MapMod.png")
      ratio = pixmap.size().height()/pixmap.size().width()
      newsize = 500
      pixmap = pixmap.scaled(newsize, int(newsize*ratio), Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
      img.setPixmap(pixmap)
      contentLayout.addWidget(img)
      
      #Finish scroll area
      layout.addWidget(scrollArea)
      
   def setupShort(self):
      layout = QVBoxLayout(self.tabShort)
      scrollArea = QScrollArea()
      
      #Set scroll area
      contentWidget = QWidget()
      contentLayout = QVBoxLayout(contentWidget)
      scrollArea.setWidget(contentWidget)
      scrollArea.setWidgetResizable(True)
      
      #Body of the tab      
      img = QLabel()
      #pixmap = QPixmap(str(current_path)+"/img/helper/Hierarchy/Mappor.png")
      pixmap = QPixmap("./img/helper/Shortcuts.png")
      ratio = pixmap.size().height()/pixmap.size().width()
      newsize = 500
      pixmap = pixmap.scaled(newsize, int(newsize*ratio), Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
      img.setPixmap(pixmap)
      contentLayout.addWidget(img)
      
      #Finish scroll area
      layout.addWidget(scrollArea)
      
   def resizeEvent(self, event):
      super().resizeEvent(event)
      width = self.width()
      tab_index = self.tab.currentIndex()
      
      # if tab_index == 0:
      #    contentWidget = self.tabMain.findChild(QWidget)
      #    img = contentWidget.findChild(QLabel)
      #    pixmap = img.pixmap()
         
      #    new_width = width - 20
      #    new_height = int(new_width * pixmap.height() / pixmap.width())
      #    new_pixmap = pixmap.scaled(new_width, new_height)
      #    img.setPixmap(new_pixmap)
      
if __name__=="__main__":
   app = QApplication(sys.argv)
    
   ex = HelpWindow()
    
   ex.show()
   sys.exit(app.exec())