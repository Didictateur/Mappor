from PyQt5.QtWidgets import * 
from PyQt5.QtCore import * 
from PyQt5.QtGui import *

class HelpWindow(QMainWindow):
   def __init__(self):
      super().__init__(self)
      self.setWindowTitle("Help")
      self.initUI()

   def initUI(self):
      self.tab = QTabWidget(self)

      self.tabTile = QTabWidget()
      self.tabDraw = QTabWidget()
      self.tabMap = QTabWidget()

      self.tab.addTab(self.tabTile, "Tile")
      self.tab.addTab(self.tabDraw, "Draw")
      self.tab.addTab(self.tabMap, "Map")

      self.setupTile()
      self.setupDraw()
      self.setupMap()

      self.setCentralWidget(self.tab)