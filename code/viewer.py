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

N = 4

def reverse(L: list) -> list:
    if L == []:
        return L
    x = L.pop()
    return [x] + reverse(L)

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
        self.fig, self.axes = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        
        self.littleFig, self.littleAxes = plt.subplots()
        self.littleCanvas = FigureCanvas(self.littleFig)
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
        self.treeWidget = QTreeWidget()
        self.treeWidget.setColumnCount(1)
        self.setTree()
        self.treeWidget.clicked.connect(self.clickedFile)
        self.treeWidget.doubleClicked.connect(self.doubleClickedFile)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.showMenu)
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
        
    def showMenu(self, pos):
        item = self.treeWidget.itemAt(pos)
        if item is not None:
            print("yay")
        
        
    def saveTile(self):
        if self.sceny != None and self.sceny.tile != None:
            Lpath = (str(root_path)+'/'+self.sceny.path).split('/')
            path = ''
            for spath in Lpath[:-1]:
                path += '/'+spath
            self.sceny.tile.save(path)
            self.sceny.littleTile = self.sceny.tile.copy()
            self.sceny.saves.append(self.sceny.tile.copy())
            self.labelStatus.showMessage("Work saved", 2000)
            self.drawLittle()
            self.drawScene(0)
    
    # draw part
    def drawDraw(self, initSceny=True):
        self.mod = "Draw" 
        self.setWindowTitle("Draw Mod")
        if initSceny:
            self.sceny = Scene()
        self.fig, self.axes = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
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
        self.treeWidget = QTreeWidget()
        self.treeWidget.setColumnCount(1)
        
        self.setTree()
        self.treeWidget.clicked.connect(self.clickedFile)
        self.treeWidget.doubleClicked.connect(self.doubleClickedFile)
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
        
    def addRowLeft(self):
        self.sceny.draw.addLeft()
        self.sceny.saves.append(self.sceny.draw.copy())
        self.drawScene(1)
    
    def addUp(self):
        self.sceny.draw.addUp()
        self.sceny.saves.append(self.sceny.draw.copy())
        self.drawScene(1)    
    
    def addDown(self):
        self.sceny.draw.addDown()
        self.sceny.saves.append(self.sceny.draw.copy())
        self.drawScene(1) 
    
    def addRight(self):
        self.sceny.draw.addRight()
        self.sceny.saves.append(self.sceny.draw.copy())
        self.drawScene(1) 
        
    def saveDraw(self):
        if self.sceny != None and self.sceny.draw != None:
            Lpath = (str(root_path)+'/'+self.sceny.path).split('/')
            path = ''
            for spath in Lpath[:-1]:
                path += '/'+spath
            self.sceny.draw.save(path)
            self.sceny.littleDraw = self.sceny.draw.copy()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.drawLittle()
            self.drawScene(1)
            
    # map part
    def drawMap(self, initSceny=True):
        self.mod = "Map" 
        self.setWindowTitle("Map Mod")
        if initSceny:
            self.sceny = Scene()
        self.fig, self.axes = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
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
        
        # Tree project
        self.treeWidget = QTreeWidget()
        self.treeWidget.setColumnCount(1)
        
        self.setTree()
        self.treeWidget.clicked.connect(self.clickedFile)
        self.treeWidget.doubleClicked.connect(self.doubleClickedFile)
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
            
    # General Part

    def switchRemove(self):
        self.remove = 1-self.remove
        
    def checkDraw(self, mod):
        if self.mod == "Tile":
            if self.sceny is not None and self.sceny.path != None:
                tile = Tile.load(str(root_path)+'/'+self.sceny.path)
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
                if mod == "Tile":
                    self.newTile()
                elif mod == "Draw":
                    self.newDraw()
                elif mod == "Map":
                    self.newMap()
        elif self.mod == "Draw":
            if self.sceny is not None and self.sceny.path != None:
                draw = Draw.load(str(root_path)+'/'+self.sceny.path)
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
                if mod == "Tile":
                    self.newTile()
                elif mod == "Draw":
                    self.newDraw()
                elif mod == "Map":
                    self.newMap()
        elif self.mod == "Map":
            if self.sceny is not None and self.sceny.path != None:
                map_ = Map.load(str(root_path)+'/'+self.sceny.path)
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
                if mod == "Tile":
                    self.newTile()
                elif mod == "Draw":
                    self.newDraw()
                elif mod == "Map":
                    self.newMap()
                
    def newTile(self, warning=0):
        if warning == 1:
            name, ok = QInputDialog.getText(self, "New Tile", "This file already existe")
        elif warning == 2:
            name, ok = QInputDialog.getText(self, "New Tile", "The chossen name is not available")
        else:
            name, ok = QInputDialog.getText(self, "New Tile", "Name your new work")
        if ok:
            if self.sceny.littlePath == None:
                path = root_path #TODO: unauthorized that case
            else:
                path = ""
                for spath in self.sceny.littlePath.split('/')[:-1]:
                    path += '/' + spath
            if '.' in name or '/' in name:
                self.newTile(2)
            elif os.path.isfile(str(path)[1:]+f"/{name}.mprt"):
                self.newTile(1)
            else:
                newTile = Tile(N, name=name)
                newTile.save(path)
                newPath = ''
                for spath in path.split('/'):
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
                self.drawTile(False)
                
    def newDraw(self, warning=0):
        if warning == 1:
            name, ok = QInputDialog.getText(self, "New Tile", "This file already existe")
        elif warning == 2:
            name, ok = QInputDialog.getText(self, "New Tile", "The chossen name is not available")
        else:
            name, ok = QInputDialog.getText(self, "New Tile", "Name your new work")
        if ok:
            if self.sceny.littlePath == None:
                path = root_path
            else:
                path = ""
                for spath in self.sceny.littlePath.split('/')[:-1]:
                    path += '/' + spath
            if '.' in name or '/' in name:
                self.newDraw(2)
            elif os.path.isfile(str(path)[1:]+f"/{name}.mprt"):
                self.newdraw(1)
            else:
                newDraw = Draw((2, 2), N, name=name)
                newDraw.save(path)
                newPath = ''
                for spath in str(path).split('/'):
                    if spath not in str(root_path).split('/'):
                        newPath += '/'+spath
                self.sceny.draw = newDraw.copy()
                self.sceny.tile = None
                self.sceny.map = None
                self.sceny.littleDraw = newDraw.copy()
                self.sceny.littleTile = None
                self.sceny.littleMap = None
                self.sceny.path = newPath
                self.sceny.littlePath = newPath
                self.drawDraw(False)
                
    def newMap(self, warning=0):
        if warning == 1:
            name, ok = QInputDialog.getText(self, "New Tile", "This file already existe")
        elif warning == 2:
            name, ok = QInputDialog.getText(self, "New Tile", "The chossen name is not available")
        else:
            name, ok = QInputDialog.getText(self, "New Tile", "Name your new work")
        if ok:
            if self.sceny.littlePath == None:
                path = root_path
            else:
                path = ""
                for spath in self.sceny.littlePath.split('/')[:-1]:
                    path += '/' + spath
            if '.' in name or '/' in name:
                self.newMap(2)
            elif os.path.isfile(str(path)[1:]+f"/{name}.mprt"):
                self.newMap(1)
            else:
                newMap = Map((2, 2), N, name=name)
                newMap.save(path)
                newPath = ''
                for spath in str(path).split('/'):
                    if spath not in str(root_path).split('/'):
                        newPath += '/'+spath
                self.sceny.map = newMap.copy()
                self.sceny.tile = None
                self.sceny.draw = None
                self.sceny.littleMap = newMap.copy()
                self.sceny.littleTile = None
                self.sceny.littleDraw = None
                self.sceny.path = newPath
                self.sceny.littlePath = newPath
                self.drawMap(False)
    
    def drawLittle(self):
        if self.sceny.littleTile != None:
            img = reverse(self.sceny.littleTile.toImg())
            IMG = np.array(img, dtype=np.uint8)
            self.littleAxes.cla()
            self.littleAxes.imshow(IMG)
            self.littleAxes.set_xlim(-0.5, len(img[0])-0.5)
            self.littleAxes.set_ylim(-0.5, len(img)-0.5)
            self.littleAxes.set_xticks([])
            self.littleAxes.set_yticks([])
        elif self.sceny.littleDraw != None:
            img = reverse(self.sceny.littleDraw.toImg())
            IMG = np.array(img, dtype=np.uint8)
            self.littleAxes.cla()
            self.littleAxes.imshow(IMG)
            self.littleAxes.set_xlim(-0.5, len(img[0])-0.5)
            self.littleAxes.set_ylim(-0.5, len(img)-0.5)
            self.littleAxes.set_xticks([])
            self.littleAxes.set_yticks([])
        elif self.sceny.littleMap != None:
            img = reverse(self.sceny.littleMap.toImg())
            IMG = np.array(img, dtype=np.uint8)
            self.littleAxes.cla()
            self.littleAxes.imshow(IMG)
            self.littleAxes.set_xlim(-0.5, len(img[0])-0.5)
            self.littleAxes.set_ylim(-0.5, len(img)-0.5)
            self.littleAxes.set_xticks([])
            self.littleAxes.set_yticks([])
        self.littleCanvas.draw()
            
    def drawScene(self, index: int):
        if self.sceny is not None and (self.sceny.tile, self.sceny.draw, self.sceny.map) != (None, None, None):
            if index == 0:
                img = reverse(self.sceny.tile.toImg())
            elif index == 1:
                img = reverse(self.sceny.draw.toImg())
            elif index == 2:
                img = reverse(self.sceny.map.toImg())
            self.YMax = len(img)-0.5
            self.XMax = len(img[0])-0.5
            IMG = np.array(img, dtype=np.uint8)
            self.axes.cla()  # Efface tous les éléments existants dans les axes
            self.axes.imshow(IMG)
            self.axes.set_xlim(self.XMin, self.XMax)
            self.axes.set_ylim(self.YMin, self.YMax)
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.canvas.draw()
        
    def selectDirectory(self):
        path_out = Path(__file__).parent.parent.joinpath('out')
        name = QFileDialog.getExistingDirectory(
            self, "Select directory", str(path_out)
        )
        if name != '':
            self.path = str(Path(name))
        else:
            self.selectDirectory()
            
    def clickedFile(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            path = selected_item.data(1, Qt.DisplayRole)
            if path.split('.')[-1] == "mprt":
                self.sceny.littleTile = Tile.load(str(root_path)+'/'+path)
                self.sceny.littleDraw = None
                self.sceny.littlePath = str(root_path)+'/'+path
            elif path.split('.')[-1] == "mprd":
                self.sceny.littleDraw = Draw.load(str(root_path)+'/'+path)
                self.sceny.littleTile = None
                self.sceny.littlePath = str(root_path)+'/'+path
        self.drawLittle()
        
    def doubleClickedFile(self): #TODO map
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            path = selected_item.data(1, Qt.DisplayRole)
            if path.split('.')[-1] == "mprt":
                tile = Tile.load(str(root_path)+'/'+path)
                i = 1048576
                if self.mod == "Tile":
                    if self.sceny.path != None and tile != self.sceny.tile and self.sceny.tile != Tile.load(str(root_path)+'/'+self.sceny.path):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Draw":
                    if self.sceny.path != None and self.sceny.draw != Draw.load(str(root_path)+'/'+self.sceny.path):
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
                    self.sceny.littleTile = Tile.load(str(root_path)+'/'+path)
                    self.sceny.littleDraw = None
                    self.sceny.path = path
                    self.sceny.saves.init()
                    self.sceny.saves.append(self.sceny.tile.copy())
                    self.drawLittle()
                    if self.mod != "Tile":
                        self.drawTile(False)
                    self.drawScene(0)
                    
            elif path.split('.')[-1] == "mprd":
                draw = Draw.load(str(root_path)+'/'+path)
                i = 1048576
                if self.mod == "Tile":
                    if self.sceny.path != None and draw != self.sceny.draw and self.sceny.draw != Draw.load(str(root_path)+'/'+self.sceny.path):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Draw":
                    if self.sceny.path != None and self.sceny.draw != Draw.load(str(root_path)+'/'+self.sceny.path):
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
                    self.sceny.littleTile = Tile.load(str(root_path)+'/'+path)
                    self.sceny.littleDraw = None
                    self.sceny.path = path
                    self.sceny.saves.init()
                    self.sceny.saves.append(self.sceny.tile.copy())
                    self.drawLittle()
                    if self.mod != "Tile":
                        self.drawTile(False)
                    self.drawScene(0)
    
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
        if self.mod == "Tile":
            saveAction.triggered.connect(self.saveTile)
        if self.mod == "Draw":
            saveAction.triggered.connect(self.saveDraw)
        if self.mod == "Map":
            saveAction.triggered.connect(self.saveMap)
        
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

        # Menu Bar
        file_menu = self.menu.addMenu("&File")
        file_menu.addAction(selectFolderAction)
        file_menu.addAction(saveAction)
        file_menu.addAction(loadAction)
        edit_menu = self.menu.addMenu("&Edit")
        edit_menu.addAction(undoAction)
        edit_menu.addAction(redoAction)
        edit_menu.addAction(newTileAction)
        edit_menu.addAction(newDrawAction)
        edit_menu.addAction(newMapAction)
        help_menu = self.menu.addMenu("&Help")
            
    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color
            self.color_label.setStyleSheet("QLabel { background-color: %s }" % color.name())
            
    def resize(self): #TODO
        self.sceny.draw.resize()
        self.sceny.saves.append(self.sceny.draw.copy())
        self.drawScene(1)
        
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
            
    # Events
    def mousePressEvent(self, event):
        if event.inaxes is not None:
            y, x = int(event.xdata + 0.5),  int(self.YMax - event.ydata)
            if self.sceny.tile != None:
                if self.current_color != None:
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
                if self.remove:
                    self.sceny.map.setTile((int(x/N), int(y/N)), None)
                    self.sceny.saves.append(self.sceny.map.copy())
                elif self.sceny.littleTile != None:
                    self.sceny.map.setTile((int(x/N), int(y/N)), self.sceny.littleTile.copy())
                    self.sceny.saves.append(self.sceny.map.copy())
                elif self.sceny.littleDraw != None:
                    self.sceny.map.addDraw((int(x/N), int(y/N)), self.sceny.littleDraw.copy())
                    self.sceny.saves.append(self.sceny.map.copy())
                
                
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