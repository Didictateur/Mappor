from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import sys
import subprocess

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.patches import Arc, Circle

from pathlib import Path

from .src.map import*

current_path = Path(__file__).parent.absolute()
root_path = current_path.parent.parent

N = 16

def reverse(L: list) -> list:
    if L == []:
        return L
    x = L.pop()
    return [x] + reverse(L)

def joinpath(rootpath: str, filepath: str, last: int=0) -> str:
    rootpath = [spath for spath in str(rootpath).split('/') if spath != '']
    filepath = [spath for spath in str(filepath).split('/') if spath != '']
    path = rootpath + filepath
    path.append("")
    return '/' + ('/').join(path[:-(last+1)])
    

class Saves:
    def __init__(self):
        self.saves = []
        self.unsaves = []
        self.maxSaves = 100
        self.type = "Tile"
        
    def init(self):
        self.saves = []
        self.unsaves = []
        
    def CZ(self):
        if len(self.saves) < 2:
            return None
        obj = self.saves.pop()
        self.unsaves.append(obj.copy())
        return self.saves[-1].copy()
    
    def CY(self):
        if self.unsaves == []:
            return None
        obj = self.unsaves.pop()
        self.saves.append(obj.copy())
        return obj
    
    def append(self, obj):
        self.saves.append(obj)
        self.unsaves = []
        self.saves = self.saves[-self.maxSaves:]
        

class Scene:
    def __init__(self) -> None:
        self.tile = None
        self.draw = None
        self.map = None
        
        self.littleTile = None
        self.littleDraw = None
        self.littleMap = None
        
        self.saves = Saves()
        self.path = None
        self.littlePath = None

    def setTile(self, path):
        self.tile = Tile.load(path)
        self.saves.init()
        self.saves.append(self.tile)
        self.path = path
        
    def setDraw(self, path):
        self.draw = Draw.load(path)
        self.saves.init()
        self.saves.append(self.draw)
        self.path = path
        
    def setMap(self, path):
        self.map = Map.load(path)
        self.saves.init()
        self.append(self.map)
        self.path = path
        
    
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.enableDarkMod()
        self.path = None
        self.mod = "Tile"
        self.showGrid = 0
        self.colorGrid = "Red"
        self.labelStatus = QStatusBar() # When little messages
        self.setStatusBar(self.labelStatus)
                
        # Menu Bar
        self.menu = self.menuBar()
        self.setMenu()
        
        self.drawTile()
        
    
    # Tile part
    def drawTile(self, initSceny=True):
        self.mod = "Tile"
        self.setWindowTitle("Tile Mod")
        if initSceny:
            self.sceny = Scene()
        if not hasattr(self, 'fig'):
            self.fig, self.axes = plt.subplots()
            self.canvas = FigureCanvas(self.fig)
            self.canvas.setFixedSize(1200, 900)
            
            self.littleFig, self.littleAxes = plt.subplots()
            self.littleCanvas = FigureCanvas(self.littleFig)
            self.littleCanvas.setFixedSize(500, 500)
            self.littleAxes.set_xticks([])
            self.littleAxes.set_yticks([])
        
        if self.path == None:
            self.selectDirectory()
                
        layout = QHBoxLayout()
        layoutV = QVBoxLayout()
        
        # Load/Saves
        layoutSaves = QHBoxLayout()
        buttonLoad = QPushButton("Load")
        buttonSave = QPushButton("Save")
        buttonSave.clicked.connect(self.saveTile)
        layoutSaves.addWidget(buttonLoad)
        layoutSaves.addWidget(buttonSave)
        layoutV.addLayout(layoutSaves)
        
        # Paint
        paintLayout = QHBoxLayout()
        self.replaceCheck = QCheckBox("Replace")
        self.replaceCheck.stateChanged.connect(lambda: self.checkChange(0))
        self.paintBucketCheck = QCheckBox("Paint Bucket")
        self.paintBucketCheck.stateChanged.connect(lambda: self.checkChange(1))
        paintLayout.addWidget(self.replaceCheck)
        paintLayout.addWidget(self.paintBucketCheck)
        layoutV.addLayout(paintLayout)
        
        # Zone de travail pour dessiner
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setSceneRect(0, 0, 40, 40)
        
        # Palette de couleurs
        colorLayout = QHBoxLayout()
        self.color_label = QLabel(" ")
        self.color_button = QPushButton("Sélectionner une couleur")
        self.color_button.clicked.connect(self.select_color)
        colorLayout.addWidget(self.color_label)
        colorLayout.addWidget(self.color_button)
        layoutV.addLayout(colorLayout)
        
        # Tree project
        try:
            self.refresh_tree_widget()
        except:
            self.treeWidget = QTreeWidget()
            self.initTreeWidget()
        layoutV.addWidget(self.treeWidget)
        
        # The little draw
        layoutV.addWidget(self.littleCanvas, stretch=1)
        
        # Sources des projets
        self.buttonFile = QPushButton("Select source", self)
        self.buttonFile.setToolTip("Select the repository to work with")
        self.buttonFile.clicked.connect(self.selectDirectory)
        layoutV.addWidget(self.buttonFile)
        
        
        # Mise en forme
        layoutH = QHBoxLayout()
        self.XMin = -0.5
        self.YMin = -0.5
        if self.sceny.tile != None:
            img = self.sceny.tile.toImg()
            self.XMax = len(img)-0.5
            self.YMax = len(img[0])-0.5
        else:
            self.XMax = 1.5
            self.YMax = 1.5
        
        self.drawScene(0)
                
        self.canvas.mpl_connect('button_press_event', self.mousePressEvent)
        
        toolbar = NavigationToolbar(self.canvas, self)
        layoutV.addWidget(toolbar)
        
        layoutH.addWidget(self.canvas, stretch=1)
        layoutH.addLayout(layoutV, stretch=1)
        
                
        central_widget = QWidget()
        central_widget.setLayout(layoutH)
        self.setCentralWidget(central_widget)
                                        
    def saveTile(self):
        if self.sceny != None and self.sceny.tile != None:
            if '.' in self.sceny.path:
                path = joinpath(root_path, self.sceny.path, 1)
            else:
                path = joinpath(root_path, self.sceny.path)
            self.sceny.tile.save(path)
            self.sceny.littleTile = self.sceny.tile.copy()
            self.sceny.saves.append(self.sceny.tile.copy())
            self.labelStatus.showMessage("Work saved", 2000)
            self.drawLittle()
            self.drawScene(0)
        else:
            self.labelStatus.showMessage("Warning: your work have not been saved, select a repository or a file", 4000)
    
    # draw part
    def drawDraw(self, initSceny=True):
        self.mod = "Draw"
        self.setWindowTitle("Draw Mod")
        if initSceny:
            self.sceny = Scene()
        self.fig, self.axes = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setFixedSize(1200, 900)
        self.littleCanvas.setFixedSize(500, 500)
        self.remove = 0
        
        self.littleFig, self.littleAxes = plt.subplots()
        self.littleCanvas = FigureCanvas(self.littleFig)
        self.littleAxes.set_xticks([])
        self.littleAxes.set_yticks([])

        layout = QHBoxLayout()
        layoutV = QVBoxLayout()
        
        # Load/Saves
        layoutSaves = QHBoxLayout()
        buttonLoad = QPushButton("Load")
        buttonSave = QPushButton("Save")
        buttonSave.clicked.connect(self.saveDraw)
        layoutSaves.addWidget(buttonLoad)
        layoutSaves.addWidget(buttonSave)
        layoutV.addLayout(layoutSaves)
        
        # Zone de travail pour dessiner
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setSceneRect(0, 0, 40, 40)
        
        # Redimensionnement
        layoutRemove = QHBoxLayout()
        removeCheck = QCheckBox("Remove tile")
        removeCheck.stateChanged.connect(self.switchRemove)
        layoutRemove.addWidget(removeCheck)
        buttonResize = QPushButton("Resize")
        buttonResize.clicked.connect(self.resize)
        layoutRemove.addWidget(buttonResize)
        layoutV.addLayout(layoutRemove)
        
        # Tree project
        try:
            self.refresh_tree_widget()
        except:
            self.treeWidget = QTreeWidget()
            self.initTreeWidget()
        layoutV.addWidget(self.treeWidget)
        
        # The little draw
        layoutV.addWidget(self.littleCanvas, stretch=1)
        
        # Sources des projets
        self.buttonFile = QPushButton("Select source", self)
        self.buttonFile.setToolTip("Select the repository to work with")
        self.buttonFile.clicked.connect(self.selectDirectory)
        layoutV.addWidget(self.buttonFile)
        
        
        # Mise en forme
        layoutH = QHBoxLayout()
        self.XMin = -0.5
        self.YMin = -0.5
        if self.sceny.draw != None:
            img = self.sceny.draw.toImg()
            self.XMax = len(img)-0.5
            self.YMax = len(img[0])-0.5
        else:
            self.XMax = 1.5
            self.YMax = 1.5
        
        self.drawScene(1)
                        
        self.canvas.mpl_connect('button_press_event', self.mousePressEvent)
        
        toolbar = NavigationToolbar(self.canvas, self)
        layoutV.addWidget(toolbar)
        
        layoutC = QHBoxLayout()
        
        buttonUp = QPushButton("Add")
        buttonUp.clicked.connect(self.addRowLeft)
        layoutC.addWidget(buttonUp)
        
        layoutCv = QVBoxLayout()
        buttonL = QPushButton("Add")
        buttonL.clicked.connect(self.addUp)
        buttonR = QPushButton("Add")
        buttonR.clicked.connect(self.addDown)
        layoutCv.addWidget(buttonL)
        layoutCv.addWidget(self.canvas, stretch=1)
        layoutCv.addWidget(buttonR)
        layoutC.addLayout(layoutCv)
        
        buttonD = QPushButton("Add")
        buttonD.clicked.connect(self.addRight)
        layoutC.addWidget(buttonD)
        
        layoutH.addLayout(layoutC)
        layoutH.addLayout(layoutV, stretch=1)
        
        central_widget = QWidget()
        central_widget.setLayout(layoutH)
        self.setCentralWidget(central_widget) 
                
    def saveDraw(self):
        if self.sceny != None and self.sceny.draw != None:
            if '.' in self.sceny.path:
                path = joinpath(root_path, self.sceny.path, 1)
            else:
                path = joinpath(root_path, self.sceny.path)
            self.sceny.draw.save(path)
            self.sceny.littleDraw = self.sceny.draw.copy()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.labelStatus.showMessage("Work saved", 2000)
            self.drawLittle()
            self.drawScene(1)
        else:
            self.labelStatus.showMessage("Warning: your work have not been saved, select a repository or a file", 4000)
            
    # map part
    def drawMap(self, initSceny=True):
        self.mod = "Map"
        self.setWindowTitle("Map Mod")
        if initSceny:
            self.sceny = Scene()
        self.fig, self.axes = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setFixedSize(1200, 900)
        self.littleCanvas.setFixedSize(500, 500)
        self.remove = 0
        
        self.littleFig, self.littleAxes = plt.subplots()
        self.littleCanvas = FigureCanvas(self.littleFig)
        self.littleAxes.set_xticks([])
        self.littleAxes.set_yticks([])

        layout = QHBoxLayout()
        layoutV = QVBoxLayout()
        
        # Load/Saves
        layoutSaves = QHBoxLayout()
        buttonLoad = QPushButton("Load")
        buttonSave = QPushButton("Save")
        buttonSave.clicked.connect(self.saveMap)
        layoutSaves.addWidget(buttonLoad)
        layoutSaves.addWidget(buttonSave)
        layoutV.addLayout(layoutSaves)
        
        # Zone de travail pour dessiner
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setSceneRect(0, 0, 40, 40)
        
        # Redimensionnement
        layoutRemove = QHBoxLayout()
        removeCheck = QCheckBox("Remove tile")
        removeCheck.stateChanged.connect(self.switchRemove)
        layoutRemove.addWidget(removeCheck)
        buttonResize = QPushButton("Resize")
        buttonResize.clicked.connect(self.resize)
        layoutRemove.addWidget(buttonResize)
        layoutV.addLayout(layoutRemove)
        
        # Grid modification
        layoutGrid = QHBoxLayout()
        
        self.gombolabel = QLabel("Select ground value")
        
        self.gombobox = QComboBox()
        for i in range(10):
            self.gombobox.addItem(str(i))
        for letter in "BSWVITDNSWE":
            self.gombobox.addItem(letter)
            
        layoutGrid.addWidget(self.gombolabel)
        layoutGrid.addWidget(self.gombobox)
        layoutV.addLayout(layoutGrid)
        
        # Tree project
        try:
            self.refresh_tree_widget()
        except:
            self.treeWidget = QTreeWidget()
            self.initTreeWidget()
        layoutV.addWidget(self.treeWidget)
        
        # The little draw
        layoutV.addWidget(self.littleCanvas, stretch=1)
        
        # Sources des projets
        self.buttonFile = QPushButton("Select source", self)
        self.buttonFile.setToolTip("Select the repository to work with")
        self.buttonFile.clicked.connect(self.selectDirectory)
        layoutV.addWidget(self.buttonFile)
        
        
        # Mise en forme
        layoutH = QHBoxLayout()
        self.XMin = -0.5
        self.YMin = -0.5
        if self.sceny.map != None:
            img = self.sceny.map.toImg()
            self.XMax = len(img)-0.5
            self.YMax = len(img[0])-0.5
        else:
            self.XMax = 1.5
            self.YMax = 1.5
        
        self.drawScene(2)
                        
        self.canvas.mpl_connect('button_press_event', self.mousePressEvent)
        
        toolbar = NavigationToolbar(self.canvas, self)
        layoutV.addWidget(toolbar)
        
        layoutC = QHBoxLayout()
        
        buttonUp = QPushButton("Add")
        buttonUp.clicked.connect(self.addRowLeft)
        layoutC.addWidget(buttonUp)
        
        layoutCv = QVBoxLayout()
        buttonL = QPushButton("Add")
        buttonL.clicked.connect(self.addUp)
        buttonR = QPushButton("Add")
        buttonR.clicked.connect(self.addDown)
        layoutCv.addWidget(buttonL)
        layoutCv.addWidget(self.canvas, stretch=1)
        layoutCv.addWidget(buttonR)
        layoutC.addLayout(layoutCv)
        
        buttonD = QPushButton("Add")
        buttonD.clicked.connect(self.addRight)
        layoutC.addWidget(buttonD)
        
        layoutH.addLayout(layoutC)
        layoutH.addLayout(layoutV, stretch=1)
        
        central_widget = QWidget()
        central_widget.setLayout(layoutH)
        self.setCentralWidget(central_widget)
        
    def saveMap(self):
        if self.sceny != None and self.sceny.map != None:
            if '.' in self.sceny.path:
                path = joinpath(root_path, self.sceny.path, 1)
            else:
                path = joinpath(root_path, self.sceny.path)
            self.sceny.map.save(path)
            self.sceny.littleMap = self.sceny.map.copy()
            self.sceny.saves.append(self.sceny.map.copy())
            self.drawLittle()
            self.drawScene(2)
        else:
            self.labelStatus.showMessage("Warning: your work have not been saved, select a repository or a file", 4000)
                                           
    # General Part
    def addRowLeft(self):
        if self.mod == "Draw":
            self.sceny.draw.addLeft()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.drawScene(1)
        elif self.mod == "Map":
            self.sceny.map.addLeft()
            self.sceny.saves.append(self.sceny.map.copy())
            self.drawScene(2)
    
    def addUp(self):
        if self.mod == "Draw":
            self.sceny.draw.addUp()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.drawScene(1)    
        elif self.mod == "Map":
            self.sceny.map.addUp()
            self.sceny.saves.append(self.sceny.map.copy())
            self.drawScene(2) 
    
    def addDown(self):
        if self.mod == "Draw":
            self.sceny.draw.addDown()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.drawScene(1) 
        elif self.mod == "Map":
            self.sceny.map.addDown()
            self.sceny.saves.append(self.sceny.map.copy())
            self.drawScene(2) 
    
    def addRight(self):
        if self.mod == "Draw":
            self.sceny.draw.addRight()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.drawScene(1)
        elif self.mod == "Map":
            self.sceny.map.addRight()
            self.sceny.saves.append(self.sceny.map.copy())
            self.drawScene(2)

    def switchRemove(self):
        self.remove = 1-self.remove
        
    def switchGrid(self):
        self.showGrid = 1-self.showGrid
        if self.mod == "Tile":
            self.drawScene(0)
        elif self.mod == "Draw":
            self.drawScene(1)
        elif self.mod == "Map":
            self.drawScene(2)
        
    def checkDraw(self, mod):
        if self.mod == "Tile":
            if self.sceny is not None and self.sceny.path != None and '.' in self.sceny.path:
                tile = Tile.load(joinpath(root_path, self.sceny.path))
                i = 1048576
                if tile != self.sceny.tile:
                    msg = QMessageBox()
                    msg.setWindowTitle("Alert")
                    msg.setText("You didn't save your work !")
                    msg.setIcon(QMessageBox.Warning)
                    msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                    msg.buttonClicked.connect(self.test)
                    i = msg.exec()
                if i == 1048576:
                    if mod == "Tile":
                        self.newTile()
                    elif mod == "Draw":
                        self.newDraw()
                    elif mod == "Map":
                        self.newMap()
            else:
                if self.sceny.path == None:
                    self.sceny.path = self.sceny.littlePath
                if mod == "Tile":
                    self.newTile()
                elif mod == "Draw":
                    self.newDraw()
                elif mod == "Map":
                    self.newMap()
        elif self.mod == "Draw":
            if self.sceny is not None and self.sceny.path != None and '.' in self.sceny.path:
                draw = Draw.load(joinpath(root_path, self.sceny.path))
                i = 1048576
                if draw != self.sceny.draw:
                    msg = QMessageBox()
                    msg.setWindowTitle("Alert")
                    msg.setText("You didn't save your work !")
                    msg.setIcon(QMessageBox.Warning)
                    msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                    msg.buttonClicked.connect(self.test)
                    i = msg.exec()
                if i == 1048576:
                    if mod == "Tile":
                        self.newTile()
                    elif mod == "Draw":
                        self.newDraw()
                    elif mod == "Map":
                        self.newMap()
            else:
                if self.sceny.path == None:
                    self.sceny.path = self.sceny.littlePath
                if mod == "Tile":
                    self.newTile()
                elif mod == "Draw":
                    self.newDraw()
                elif mod == "Map":
                    self.newMap()
        elif self.mod == "Map":
            if self.sceny is not None and self.sceny.path != None and '.' in self.sceny.path:
                map_ = Map.load(joinpath(root_path, self.sceny.path))
                i = 1048576
                if map_ != self.sceny.map:
                    msg = QMessageBox()
                    msg.setWindowTitle("Alert")
                    msg.setText("You didn't save your work !")
                    msg.setIcon(QMessageBox.Warning)
                    msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                    msg.buttonClicked.connect(self.test)
                    i = msg.exec()
                if i == 1048576:
                    if mod == "Tile":
                        self.newTile()
                    elif mod == "Draw":
                        self.newDraw()
                    elif mod == "Map":
                        self.newMap()
            else:
                if self.sceny.path == None:
                    self.sceny.path = self.sceny.littlePath
                if mod == "Tile":
                    self.newTile()
                elif mod == "Draw":
                    self.newDraw()
                elif mod == "Map":
                    self.newMap()
                
    def newTile(self, warning=0):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            path = selected_item.data(1, Qt.DisplayRole)
        if warning == 1:
            name, ok = QInputDialog.getText(self, "New Tile", "This file already existe")
        elif warning == 2:
            name, ok = QInputDialog.getText(self, "New Tile", "The chossen name is not available")
        else:
            name, ok = QInputDialog.getText(self, "New Tile", "Name your new work")
        if ok:
            if '.' in path:
                path = joinpath("", path, 1)
            if '.' in name or '/' in name or name == '':
                self.newTile(2)
            elif os.path.isfile(str(path)[1:]+f"/{name}.mprt"):
                self.newTile(1)
            else:
                newTile = Tile(N, name=name)
                newTile.save(joinpath(root_path, path))
                newPath = ''
                for spath in str(path).split('/'):
                    if spath not in str(root_path).split('/'):
                        newPath += '/'+spath
                self.sceny.tile = newTile.copy()
                self.sceny.draw = None
                self.sceny.map = None
                self.sceny.littleTile = newTile.copy()
                self.sceny.littleDraw = None
                self.sceny.littleMap = None
                self.sceny.path = newPath
                self.sceny.littlePath = newPath
                self.refreshTree()
                self.drawTile(False)
                
    def newDraw(self, warning=0):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            path = selected_item.data(1, Qt.DisplayRole)
        if warning == 1:
            name, ok = QInputDialog.getText(self, "New Draw", "This file already existe")
        elif warning == 2:
            name, ok = QInputDialog.getText(self, "New Draw", "The chossen name is not available")
        else:
            name, ok = QInputDialog.getText(self, "New Draw", "Name your new work")
        if ok:
            if '.' in path:
                path = joinpath("", path, 1)
            if '.' in name or '/' in name or name == '':
                self.newDraw(2)
            elif os.path.isfile(str(path)[1:]+f"/{name}.mprt"):
                self.newDraw(1)
            else:
                newDraw = Draw((2, 2), N, name=name)
                newDraw.save(joinpath(root_path, path))
                newPath = ''
                for spath in str(path).split('/'):
                    if spath not in str(root_path).split('/'):
                        newPath += '/'+spath
                self.sceny.tile = None
                self.sceny.draw = newDraw.copy()
                self.sceny.map = None
                self.sceny.littleTile = None
                self.sceny.littleDraw = newDraw.copy()
                self.sceny.littleMap = None
                self.sceny.path = newPath
                self.sceny.littlePath = newPath
                self.refreshTree()
                self.drawDraw(False)
                
    def newMap(self, warning=0):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            path = selected_item.data(1, Qt.DisplayRole)
        if warning == 1:
            name, ok = QInputDialog.getText(self, "New Map", "This file already existe")
        elif warning == 2:
            name, ok = QInputDialog.getText(self, "New Map", "The chossen name is not available")
        else:
            name, ok = QInputDialog.getText(self, "New Map", "Name your new work")
        if ok:
            if '.' in path:
                path = joinpath("", path, 1)
            if '.' in name or '/' in name or name == '':
                self.newMap(2)
            elif os.path.isfile(str(path)[1:]+f"/{name}.mprp"):
                self.newMap(1)
            else:
                newMap = Map((2, 2), N, name=name)
                newMap.save(joinpath(root_path, path))
                newPath = ''
                for spath in str(path).split('/'):
                    if spath not in str(root_path).split('/'):
                        newPath += '/'+spath
                self.sceny.tile = None
                self.sceny.draw = None
                self.sceny.map = newMap.copy()
                self.sceny.littleTile = None
                self.sceny.littleDraw = None
                self.sceny.littleMap = newMap.copy()
                self.sceny.path = newPath
                self.sceny.littlePath = newPath
                self.refreshTree()
                self.drawMap(False)
    
    def newFolder(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            path = selected_items[0].data(1, Qt.DisplayRole)
            if str(path)[0] == '/':
                path = selected_items[0].data(0, Qt.DisplayRole)
            path = joinpath(root_path, path)
            if '.' in str(path):
                path = '/'.join(str(path).split('/')[:-1])
            self.createFolder(path)
            
    def createFolder(self, path, warning=0):
        if warning == 1:
            name, ok = QInputDialog.getText(self, "New Folder", "This file already existe")
        elif warning == 2:
            name, ok = QInputDialog.getText(self, "New Folder", "The chossen name is not available")
        else:
            name, ok = QInputDialog.getText(self, "New Folder", "Name your new folder")
        if ok:
            if '.' in name or '/' in name or name == '':
                self.createFolder(path, 2)
            elif os.path.isdir(joinpath(path, name)):
                self.createFolder(path, 1)
            else:
                os.mkdir(joinpath(path, name))
                self.labelStatus.showMessage("Folder created", 2000)
                self.refreshTree()
            
    def delete(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            path = selected_items[0].data(1, Qt.DisplayRole)
            if str(path)[0] == '/':
                path = selected_items[0].data(0, Qt.DisplayRole)
            path = joinpath(root_path, path)
            name = str(path).split('/')[-1]
            
            i = 65536 #No value
            msg = QMessageBox()
            msg.setWindowTitle("Alert")
            msg.setText(f"Are-you sure you want to delete {name} ?")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            msg.buttonClicked.connect(self.test)
            i = msg.exec()
            
            if i == 16384: #Yes value
                if os.path.isdir(path):
                    os.removedirs(path)
                    self.labelStatus.showMessage("Folder deleted", 2000)
                else:
                    os.remove(path)
                    self.labelStatus.showMessage("File deleted", 2000)
                self.refreshTree()
                
        
    
    def drawLittle(self):
        if self.sceny.littleTile != None:
            img = reverse(self.sceny.littleTile.toImg())
            IMG = np.array(img, dtype=np.uint8)
            self.littleAxes.cla()
            self.littleAxes.imshow(IMG, interpolation="nearest")
            self.littleAxes.set_xlim(-0.5, len(img[0])-0.5)
            self.littleAxes.set_ylim(-0.5, len(img)-0.5)
            self.littleAxes.set_xticks([])
            self.littleAxes.set_yticks([])
        elif self.sceny.littleDraw != None:
            img = reverse(self.sceny.littleDraw.toImg())
            IMG = np.array(img, dtype=np.uint8)
            self.littleAxes.cla()
            self.littleAxes.imshow(IMG, interpolation="nearest")
            self.littleAxes.set_xlim(-0.5, len(img[0])-0.5)
            self.littleAxes.set_ylim(-0.5, len(img)-0.5)
            self.littleAxes.set_xticks([])
            self.littleAxes.set_yticks([])
        elif self.sceny.littleMap != None:
            img = reverse(self.sceny.littleMap.toImg())
            IMG = np.array(img, dtype=np.uint8)
            self.littleAxes.cla()
            self.littleAxes.imshow(IMG, interpolation="nearest")
            self.littleAxes.set_xlim(-0.5, len(img[0])-0.5)
            self.littleAxes.set_ylim(-0.5, len(img)-0.5)
            self.littleAxes.set_xticks([])
            self.littleAxes.set_yticks([])
        self.littleCanvas.draw()
            
    def drawScene(self, index: int):
        if self.sceny is not None and (self.sceny.tile, self.sceny.draw, self.sceny.map) != (None, None, None):
            if index == 0:
                img = reverse(self.sceny.tile.toImg())
                name = self.sceny.tile.name
            elif index == 1:
                img = reverse(self.sceny.draw.toImg())
                name = self.sceny.draw.name
            elif index == 2:
                img = reverse(self.sceny.map.toImg())
                name = self.sceny.map.name
            self.XMin = -0.5
            self.YMin = -0.5
            self.YMax = len(img) - 0.5
            self.XMax = len(img[0]) - 0.5
            IMG = np.array(img, dtype=np.uint8)
            self.axes.cla()
            self.axes.imshow(IMG, interpolation="nearest")
            self.axes.set_xlim(self.XMin, self.XMax)
            self.axes.set_ylim(self.YMin, self.YMax)
            self.axes.set_title(name)
            e = 1
            if self.mod == "Draw":
                e = self.sceny.draw.tileSize
            if self.mod == "Map":
                e = self.sceny.map.tileSize
            if self.showGrid:
                self.axes.set_xticks([i*e - 0.5 for i in range(int(len(img[0])/e))])
                self.axes.set_yticks([i*e - 0.5 for i in range(int(len(img)/e))])
                self.axes.set_xticklabels([])
                self.axes.set_yticklabels([])
                self.axes.grid(True, color=self.colorGrid, alpha=0.75)
                if self.mod == "Map":
                    n, m = self.sceny.map.size
                    for i in range(n):
                        for j in range(m):
                            self.axes.text((j+0.4)*e, self.YMax - (i+0.6)*e, self.sceny.map.ground.tiles[i][j], color=self.colorGrid)
            else:
                self.axes.set_xticks([])
                self.axes.set_yticks([])
        else:
            self.axes.set_xticks([])
            self.axes.set_yticks([])
        self.canvas.draw()
        
    def selectDirectory(self):
        path_out = Path(__file__).parent.parent.joinpath('out')
        name = QFileDialog.getExistingDirectory(
            self, "Select directory", str(path_out)
        )
        if name != '':
            root_path = str(Path(name))
            self.path = str(Path(name))
    
    def test(self, i):
        return i.text()
    
    def setMenu(self):
        
        # Actions
        #folderSelect
        selectFolderAction = QAction("Select folder", self)
        selectFolderAction.triggered.connect(self.selectDirectory)

        #save
        saveAction = QAction("Save", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.triggered.connect(self.save)
        
        #load
        loadAction = QAction("Load", self)
        
        #undo
        undoAction = QAction("Undo", self)
        undoAction.setShortcut("Ctrl+Z")
        undoAction.triggered.connect(self.undo)
        
        #redo
        redoAction = QAction("Redo", self)
        redoAction.setShortcut("Ctrl+Y")
        redoAction.triggered.connect(self.redo)
        
        #new
        newTileAction = QAction("New Tile", self)
        newTileAction.setShortcut("Ctrl+T")
        newTileAction.triggered.connect(lambda: self.checkDraw("Tile"))
        newDrawAction = QAction("New Draw", self)
        newDrawAction.setShortcut("Ctrl+D")
        newDrawAction.triggered.connect(lambda: self.checkDraw("Draw"))
        newMapAction = QAction("New Map", self)
        newMapAction.setShortcut("Ctrl+M")
        newMapAction.triggered.connect(lambda: self.checkDraw("Map"))
        
        #show grid
        showGridAction = QAction("Show/Hide grid", self)
        showGridAction.setShortcut("Tab")
        showGridAction.triggered.connect(self.switchGrid)
        
        #color grid
        setColorGridAction = QAction("Set grid color", self)
        setColorGridAction.triggered.connect(self.openColorMenu)     

        # Menu Bar
        file_menu = self.menu.addMenu("&File")
        file_menu.addAction(selectFolderAction)
        file_menu.addSeparator()
        file_menu.addAction(saveAction)
        file_menu.addAction(loadAction)
        file_menu.addSeparator()
        file_menu.addAction(newTileAction)
        file_menu.addAction(newDrawAction)
        file_menu.addAction(newMapAction)
        
        edit_menu = self.menu.addMenu("&Edit")
        edit_menu.addAction(undoAction)
        edit_menu.addAction(redoAction)
        
        settingsMenu = self.menu.addMenu("&Settings")
        settingsMenu.addAction(showGridAction)
        settingsMenu.addAction(setColorGridAction)
        
        help_menu = self.menu.addMenu("&Help")
            
    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color
            self.color_label.setStyleSheet("QLabel { background-color: %s }" % color.name())
            
    def resize(self):
        if self.mod == "Draw":
            self.sceny.draw.resize()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.drawScene(1)
        elif self.mod == "Map":
            self.sceny.map.resize()
            self.sceny.saves.append(self.sceny.map.copy())
            self.drawScene(2)
        
    def setTree(self) -> None:
        tree = Tree(self.path.split('/')[-1])
        tree.value = self.path.split('/')[-1]
        tree.init(self.path)
        
        root_item = QTreeWidgetItem(self.treeWidget, [self.path.split('/')[-1], self.path])
        for c in tree.child:
            self.complete(c, root_item)
                        
    def complete(self, tree, Qtree):
        item = QTreeWidgetItem(Qtree, [tree.name, tree.value])
        citem = [item]
        if tree.child != None:
            for c in tree.child:
                self.complete(c, item)                
            
    def undo(self):
        obj = self.sceny.saves.CZ()
        if obj != None:
            if self.mod == "Tile":
                self.sceny.tile = obj.copy()
                self.drawScene(0)
            elif self.mod == "Draw":
                self.sceny.draw = obj.copy()
                self.drawScene(1)
            elif self.mod == "Map":
                self.sceny.map = obj.copy()
                self.drawScene(2)
                
    def redo(self):
        obj = self.sceny.saves.CY()
        if obj != None:
            if self.mod == "Tile":
                self.sceny.tile = obj.copy()
                self.drawScene(0)
            elif self.mod == "Draw":
                self.sceny.draw = obj.copy()
                self.drawScene(1)
            elif self.mod == "Map":
                self.sceny.map = obj.copy()
                self.drawScene(2)
                
    def enableDarkMod(self):
        plt.style.use("dark_background")
        self.setStyle(QStyleFactory.create("Fusion"))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)
        
    def save(self):
        if self.mod == "Tile":
            self.saveTile()
        elif self.mod == "Draw":
            self.saveDraw()
        elif self.mod == "Map":
            self.saveMap()
            
    # Tree events
    def initTreeWidget(self):
        self.treeWidget.clear()
        self.treeWidget.setColumnCount(1)
        self.setTree()
        self.treeWidget.clicked.connect(self.clickedFile)
        self.treeWidget.doubleClicked.connect(self.doubleClickedFile)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.showMenu)
        
    def refreshTree(self):
        expanded_states = {}
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            expanded_states[i] = item.isExpanded()

        self.treeWidget.clear()
        self.treeWidget.setColumnCount(1)
        self.setTree()
        root_item = self.treeWidget.topLevelItem(0)
        root_item.setExpanded(True)

        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            if i in expanded_states and expanded_states[i]:
                item.setExpanded(True)
                
    def getExpanded(self, item):
        L = []
        if item.isExpanded():
            L.append(item.text())
        for child in item.Child:
            L += self.getExpanded(child)
        return L
    
    def clickedFile(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            path = selected_item.data(1, Qt.DisplayRole)
            if path.split('.')[-1] == "mprt":
                self.sceny.littleTile = Tile.load(joinpath(root_path, path))
                self.sceny.littleDraw = None
                self.sceny.littleMap = None
                self.sceny.littlePath = path
            elif path.split('.')[-1] == "mprd":
                self.sceny.littleTile = None
                self.sceny.littleDraw = Draw.load(joinpath(root_path, path))
                self.sceny.littlePath = path
            elif path.split('.')[-1] == "mprp":
                self.sceny.littleTile = None
                self.sceny.littleDraw = None
                self.sceny.littleMap = Map.load(joinpath(root_path, path))
                self.sceny.littlePath = path
        self.drawLittle()
        
    def showMenu(self, position):
        item = self.treeWidget.itemAt(position)
        path = item.data(1, Qt.DisplayRole)
        if self.sceny.path == None or not '.' in self.sceny.path:
            if self.sceny.littlePath == None:
                self.sceny.littlePath = path
        if item is not None:
            menu = QMenu()
            
            #New folder
            newFolderAction = QAction("New Folder", self)
            newFolderAction.triggered.connect(self.newFolder)
            
            #New object
            newTileAction = QAction("New Tile", self)
            newTileAction.triggered.connect(lambda: self.checkDraw("Tile"))
            
            #New object
            newDrawAction = QAction("New Draw", self)
            newDrawAction.triggered.connect(lambda: self.checkDraw("Draw"))
            
            #New object
            newMapAction = QAction("New Map", self)
            newMapAction.triggered.connect(lambda: self.checkDraw("Map"))
            
            #Delete object
            deletAction = QAction("Delete", self)
            deletAction.triggered.connect(self.delete)
            
            menu.addAction(newFolderAction)
            menu.addAction(newTileAction)
            menu.addAction(newDrawAction)
            menu.addAction(newMapAction)
            menu.addAction(deletAction)
            
            menu.exec_(self.treeWidget.mapToGlobal(position))
    
    def openColorMenu(self):
        colorMenu = QMenu()
        
        redAction = QAction("Red", self)
        greenAction = QAction("Green", self)
        blueAction = QAction("Blue", self)
        
        colorMenu.addAction(redAction)
        colorMenu.addAction(greenAction)
        colorMenu.addAction(blueAction)
        
        color = colorMenu.exec_(QCursor.pos()).text()
        if color in {"Red", "Green", "Blue"}:
            self.colorGrid = color
            if self.mod == "Tile":
                self.drawScene(0)
            elif self.mod == "Draw":
                self.drawScene(1)
            elif self.mod == "Map":
                self.drawScene(2)
            
            
    # Events
    def mousePressEvent(self, event):
        if event.inaxes is not None:
            y, x = int(event.xdata + 0.5),  int(self.YMax - event.ydata)
            if self.sceny.tile != None:
                if self.current_color != None:
                    if self.replaceCheck.isChecked():
                        self.sceny.tile.replace((x, y), [self.current_color.red(), self.current_color.green(), self.current_color.blue()])
                    elif self.paintBucketCheck.isChecked():
                        self.sceny.tile.paintBuck((x, y), [self.current_color.red(), self.current_color.green(), self.current_color.blue()])
                    else:
                        self.sceny.tile.setPixel((x, y), [self.current_color.red(), self.current_color.green(), self.current_color.blue()])
                    self.sceny.saves.append(self.sceny.tile.copy())
                self.drawScene(0)
            elif self.sceny.draw != None:
                if self.remove:
                    self.sceny.draw.setTile((int(x/N), int(y/N)), None)
                    self.sceny.saves.append(self.sceny.draw.copy())
                elif self.sceny.littleTile != None:
                    self.sceny.draw.setTile((int(x/N), int(y/N)), self.sceny.littleTile.copy())
                    self.sceny.saves.append(self.sceny.draw.copy())
                self.drawScene(1)
            elif self.sceny.map != None:
                if self.showGrid:
                    value = self.gombobox.currentText()
                    self.sceny.map.ground.tiles[int(x/N)][int(y/N)] = value
                elif self.remove:
                    self.sceny.map.setTile((int(x/N), int(y/N)), None)
                    self.sceny.saves.append(self.sceny.map.copy())
                elif self.sceny.littleTile != None:
                    self.sceny.map.setTile((int(x/N), int(y/N)), self.sceny.littleTile.copy())
                    self.sceny.saves.append(self.sceny.map.copy())
                elif self.sceny.littleDraw != None:
                    self.sceny.map.addDraw((int(x/N), int(y/N)), self.sceny.littleDraw.copy())
                    self.sceny.saves.append(self.sceny.map.copy())
                self.drawScene(2)
                
    def doubleClickedFile(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            path = selected_item.data(1, Qt.DisplayRole)
            if path.split('.')[-1] == "mprt":
                tile = Tile.load(joinpath(root_path, path))
                i = 1048576
                if self.mod == "Tile":
                    if self.sceny.path != None and tile != self.sceny.tile and self.sceny.tile != Tile.load(joinpath(root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Draw":
                    if self.sceny.path != None and self.sceny.draw != Draw.load(joinpath(root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Map":
                    if self.sceny.path != None and self.sceny.map != Map.load(joinpath(root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                if i == 1048576: # Button for 'ignore'... 
                    self.sceny.tile = tile
                    self.sceny.draw = None 
                    self.sceny.littleTile = Tile.load(joinpath(root_path, path))
                    self.sceny.littleDraw = None
                    self.sceny.path = path
                    self.sceny.saves.init()
                    self.sceny.saves.append(self.sceny.tile.copy())
                    self.drawLittle()
                    if self.mod != "Tile":
                        self.drawTile(False)
                    self.drawScene(0)
                    
            elif path.split('.')[-1] == "mprd":
                draw = Draw.load(joinpath(root_path, path))
                i = 1048576
                if self.mod == "Tile":
                    if self.sceny.path != None and self.sceny.tile != Tile.load(joinpath(root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Draw":
                    if self.sceny.path != None and draw != self.sceny.draw and self.sceny.draw != Draw.load(joinpath(root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Map":
                    if self.sceny.path != None and self.sceny.map != Map.load(joinpath(root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                if i == 1048576: # Button for 'ignore'... 
                    self.sceny.draw = draw
                    self.sceny.tile = None 
                    self.sceny.map = None
                    self.sceny.littleDraw = Draw.load(joinpath(root_path, path))
                    self.sceny.littleTile = None
                    self.sceny.littleMap = None
                    self.sceny.path = path
                    self.sceny.saves.init()
                    self.sceny.saves.append(self.sceny.draw.copy())
                    self.drawLittle()
                    if self.mod != "Draw":
                        self.drawDraw(False)
                    self.drawScene(1)
                            
            elif path.split('.')[-1] == "mprp":
                map_ = Map.load(joinpath(root_path, path))
                i = 1048576
                if self.mod == "Tile":
                    if self.sceny.path != None and self.sceny.tile != Tile.load(joinpath(root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Draw":
                    if self.sceny.path != None and self.sceny.draw != Draw.load(joinpath(root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Map":
                    if self.sceny.path != None and map_ != self.sceny.map and self.sceny.map != Map.load(joinpath(root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                if i == 1048576: # Button for 'ignore'... 
                    self.sceny.tile = None 
                    self.sceny.draw = None
                    self.sceny.map = map_
                    self.sceny.littleDraw = None
                    self.sceny.littleTile = None
                    self.sceny.littleMap = Map.load(joinpath(root_path, path))
                    self.sceny.path = path
                    self.sceny.saves.init()
                    self.sceny.saves.append(self.sceny.map.copy())
                    self.drawLittle()
                    if self.mod != "Map":
                        self.drawMap(False)
                    self.drawScene(2)
    
    def checkChange(self, box: int=0):
        if self.replaceCheck.isChecked() and self.paintBucketCheck.isChecked():
            if box == 0:
                self.paintBucketCheck.setChecked(False)
            else:
                self.replaceCheck.setChecked(False)
                
# Tree class

class Tree:
    def __init__(self, name: str=""):
        self.name = name
        self.value = ""
        self.child: list[object] = None
    
    def init(self, path) -> None:
        if os.path.isdir(path):
            self.child = []
            for file in os.listdir(path):
                self.child.append(Tree(file))
                self.child[-1].value = self.value + "/" + file
                self.child[-1].init(path+'/'+file)


            
if __name__=="__main__":
    app = QApplication(sys.argv)
    
    ex = MainWindow()
    
    ex.show()
    sys.exit(app.exec())