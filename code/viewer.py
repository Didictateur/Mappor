from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import sys

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.patches import Arc, Circle

from pathlib import Path

from .src.map import*
from .help import *
from .tree import *
from .QTree import *

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
        self.maxSaves = 1000
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
        self.dragPos = []
        self.root_path = ""
        self.enableDarkMod()
        self.path = None
        self.mod = "Tile"
        self.showGrid = 0
        self.colorGrid = "Red"
        self.labelStatus = QStatusBar() # When little messages
        self.setStatusBar(self.labelStatus)
        self.copy = None
        
        self.selectDirectory()
        self.treeWidget = QTree()
        self.initTreeWidget()
        self.frame = self.getTreeFrame()
        self.treeWidget.itemDropped.connect(self.updateFrame)
        self.treeWidget.itemMoved.connect(self.resetFrame)
                
        # Menu Bar
        self.menu = self.menuBar()
        self.setMenu()
        
        self.drawTile()
        
    
    # Tile part
    def drawTile(self, initSceny=True, initCeiling=True, initDrag=True):
        self.mod = "Tile"
        self.setWindowTitle("Tile Mod")
        self.action = None
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
        
        # Ceiling, Hold and drag
        layoutC = QHBoxLayout()
        if initCeiling:
            self.checkCeiling = QCheckBox("Edit ceiling")
            self.checkCeiling.stateChanged.connect(lambda: self.drawTile(False, False, not self.checkDrag.isChecked()))
            self.checkCeiling.setShortcut("Ctrl+A")
        layoutC.addWidget(self.checkCeiling)
        
        if initDrag:
            self.checkDrag = QCheckBox("Hold and Drag")
            self.checkDrag.setShortcut("Ctrl+H")
        layoutC.addWidget(self.checkDrag)
        layoutV.addLayout(layoutC)
        
        # Paint
        paintLayout = QHBoxLayout()
        self.replaceCheck = QCheckBox("Replace")
        self.replaceCheck.setShortcut("1")
        self.replaceCheck.stateChanged.connect(lambda: self.checkChange(0))
        self.paintBucketCheck = QCheckBox("Paint Bucket")
        self.paintBucketCheck.setShortcut("2")
        self.paintBucketCheck.stateChanged.connect(lambda: self.checkChange(1))
        self.superPaintBucketCheck = QCheckBox("Super Paint Bucket")
        self.superPaintBucketCheck.setShortcut("3")
        self.superPaintBucketCheck.stateChanged.connect(lambda: self.checkChange(2))
        paintLayout.addWidget(self.replaceCheck)
        paintLayout.addWidget(self.paintBucketCheck)
        paintLayout.addWidget(self.superPaintBucketCheck)
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
        
        # Tree Widget
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
        
        self.drawScene(0, True)
                
        self.canvas.mpl_connect('button_press_event', self.mousePressEvent)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_release_event', self.mouseReleaseEvent)
        
        toolbar = NavigationToolbar(self.canvas, self)
        self.setShortcuts(toolbar)
        toolbar.actionTriggered.connect(self.updateAction)
        layoutV.addWidget(toolbar)
        
        layoutH.addWidget(self.canvas, stretch=1)
        layoutH.addLayout(layoutV, stretch=1)
        
                
        central_widget = QWidget()
        central_widget.setLayout(layoutH)
        self.setCentralWidget(central_widget)
                                        
    def saveTile(self):
        if self.sceny != None and self.sceny.tile != None:
            if '.' in self.sceny.path:
                path = joinpath(self.root_path, self.sceny.path, 1)
            else:
                path = joinpath(self.root_path, self.sceny.path)
            self.sceny.tile.save(path)
            self.sceny.saves.append(self.sceny.tile.copy())
            self.labelStatus.showMessage("Work saved", 2000)
            self.drawLittle()
            self.drawScene(0)
        else:
            self.labelStatus.showMessage("Warning: your work have not been saved, select a repository or a file", 4000)
    
    # draw part
    def drawDraw(self, initSceny=True, initCeiling=True):
        self.mod = "Draw"
        self.setWindowTitle("Draw Mod")
        self.action = None
        if initSceny:
            self.sceny = Scene()
        if not hasattr(self, 'fig'):
            self.fig, self.axes = plt.subplots()
            self.canvas = FigureCanvas(self.fig)
            
            self.littleFig, self.littleAxes = plt.subplots()
            self.littleCanvas = FigureCanvas(self.littleFig)
            self.littleAxes.set_xticks([])
            self.littleAxes.set_yticks([])
        
        self.canvas.setFixedSize(1000, 800)
        self.littleCanvas.setFixedSize(500, 500)
        self.remove = 0

        layout = QHBoxLayout()
        layoutV = QVBoxLayout()
        
        # Ceiling
        if initCeiling:
            self.checkCeiling = QCheckBox("Show ceiling")
            self.checkCeiling.stateChanged.connect(lambda: self.drawDraw(False, False))
            self.checkCeiling.setShortcut("Ctrl+A")
        layoutV.addWidget(self.checkCeiling)
        
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
        
        self.drawScene(1, True)
                        
        self.canvas.mpl_connect('button_press_event', self.mousePressEvent)
        
        toolbar = NavigationToolbar(self.canvas, self)
        self.setShortcuts(toolbar)
        toolbar.actionTriggered.connect(self.updateAction)
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
                path = joinpath(self.root_path, self.sceny.path, 1)
            else:
                path = joinpath(self.root_path, self.sceny.path)
            self.sceny.draw.save(path)
            self.sceny.saves.append(self.sceny.draw.copy())
            self.labelStatus.showMessage("Work saved", 2000)
            self.drawLittle()
            self.drawScene(1)
        else:
            self.labelStatus.showMessage("Warning: your work have not been saved, select a repository or a file", 4000)
            
    # map part
    def drawMap(self, initSceny=True, initCeiling=True):
        self.mod = "Map"
        self.setWindowTitle("Map Mod")
        self.action = None
        if initSceny:
            self.sceny = Scene()
        if not hasattr(self, 'fig'):
            self.fig, self.axes = plt.subplots()
            self.canvas = FigureCanvas(self.fig)
            
            self.littleFig, self.littleAxes = plt.subplots()
            self.littleCanvas = FigureCanvas(self.littleFig)
            self.littleAxes.set_xticks([])
            self.littleAxes.set_yticks([])
        
        self.canvas.setFixedSize(1000, 800)
        self.littleCanvas.setFixedSize(500, 500)
        self.remove = 0

        layout = QHBoxLayout()
        layoutV = QVBoxLayout()
        
        # Ceiling
        if initCeiling:
            self.checkCeiling = QCheckBox("Show ceiling")
            self.checkCeiling.stateChanged.connect(lambda: self.drawMap(False, False))
            self.checkCeiling.setShortcut("Ctrl+A")
        layoutV.addWidget(self.checkCeiling)
        
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
        for letter in "BSWVITDNSWEX":
            self.gombobox.addItem(letter)
            
        layoutGrid.addWidget(self.gombolabel)
        layoutGrid.addWidget(self.gombobox)
        layoutV.addLayout(layoutGrid)
        
        # Tree project
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
        
        self.drawScene(2, True)
                        
        self.canvas.mpl_connect('button_press_event', self.mousePressEvent)
        
        toolbar = NavigationToolbar(self.canvas, self)
        self.setShortcuts(toolbar)
        toolbar.actionTriggered.connect(self.updateAction)
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
                path = joinpath(self.root_path, self.sceny.path, 1)
            else:
                path = joinpath(self.root_path, self.sceny.path)
            self.sceny.map.save(path)
            self.sceny.saves.append(self.sceny.map.copy())
            self.labelStatus.showMessage("Work saved", 2000)
            self.drawLittle()
            self.drawScene(2)
        else:
            self.labelStatus.showMessage("Warning: your work have not been saved, select a repository or a file", 4000)
                                           
    # General Part
    def setShortcuts(self, toolbar):
        for action in toolbar.actions():
            if action.text() == "Zoom":
                action.setShortcut("Alt+Z")
            if action.text() == "Pan":
                action.setShortcut("Alt+Y")
    
    def addRowLeft(self):
        if self.mod == "Draw":
            self.sceny.draw.addLeft()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.drawScene(1, True)
        elif self.mod == "Map":
            self.sceny.map.addLeft()
            self.sceny.saves.append(self.sceny.map.copy())
            self.drawScene(2, True)
    
    def addUp(self):
        if self.mod == "Draw":
            self.sceny.draw.addUp()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.drawScene(1, True)    
        elif self.mod == "Map":
            self.sceny.map.addUp()
            self.sceny.saves.append(self.sceny.map.copy())
            self.drawScene(2, True) 
    
    def addDown(self):
        if self.mod == "Draw":
            self.sceny.draw.addDown()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.drawScene(1, True) 
        elif self.mod == "Map":
            self.sceny.map.addDown()
            self.sceny.saves.append(self.sceny.map.copy())
            self.drawScene(2, True) 
    
    def addRight(self):
        if self.mod == "Draw":
            self.sceny.draw.addRight()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.drawScene(1, True)
        elif self.mod == "Map":
            self.sceny.map.addRight()
            self.sceny.saves.append(self.sceny.map.copy())
            self.drawScene(2, True)

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
                tile = Tile.load(joinpath(self.root_path, self.sceny.path))
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
                draw = Draw.load(joinpath(self.root_path, self.sceny.path))
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
                map_ = Map.load(joinpath(self.root_path, self.sceny.path))
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
                treeFrame = self.getTreeFrame()
                newTile = Tile(N, name=name)
                newTile.save(joinpath(self.root_path, path))
                newPath = ''
                for spath in str(path).split('/'):
                    if spath not in str(self.root_path).split('/'):
                        newPath += '/'+spath
                newPath += f"/{name}.mprt"
                self.sceny.tile = newTile.copy()
                self.sceny.draw = None
                self.sceny.map = None
                self.sceny.littleTile = newTile.copy()
                self.sceny.littleDraw = None
                self.sceny.littleMap = None
                self.sceny.path = newPath
                self.sceny.littlePath = newPath
                self.setTreeframe(treeFrame)
                self.drawTile(False, False)
                
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
                treeFrame = self.getTreeFrame()
                newDraw = Draw((2, 2), N, name=name)
                newDraw.save(joinpath(self.root_path, path))
                newPath = ''
                for spath in str(path).split('/'):
                    if spath not in str(self.root_path).split('/'):
                        newPath += '/'+spath
                newPath += f"/{name}.mprd"
                self.sceny.tile = None
                self.sceny.draw = newDraw.copy()
                self.sceny.map = None
                self.sceny.littleTile = None
                self.sceny.littleDraw = newDraw.copy()
                self.sceny.littleMap = None
                self.sceny.path = newPath
                self.sceny.littlePath = newPath
                self.setTreeframe(treeFrame)
                self.drawDraw(False, False)
                
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
                treeFrame = self.getTreeFrame()
                newMap = Map((2, 2), N, name=name)
                newMap.save(joinpath(self.root_path, path))
                newPath = ''
                for spath in str(path).split('/'):
                    if spath not in str(self.root_path).split('/'):
                        newPath += '/'+spath
                newPath += f"/{name}.mprp"
                self.sceny.tile = None
                self.sceny.draw = None
                self.sceny.map = newMap.copy()
                self.sceny.littleTile = None
                self.sceny.littleDraw = None
                self.sceny.littleMap = newMap.copy()
                self.sceny.path = newPath
                self.sceny.littlePath = newPath
                self.setTreeframe(treeFrame)
                self.drawMap(False, False)
    
    def newFolder(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            path = selected_items[0].data(1, Qt.DisplayRole)
            if '.' in str(path):
                path = '/'.join(str(path).split('/')[:-1])
            self.createFolder(joinpath(self.root_path, path))
            
    def createFolder(self, path, warning=0): #
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
                instantFrame = self.getTreeFrame()
                os.mkdir(joinpath(path, name))
                self.labelStatus.showMessage("Folder created", 2000)
                self.setTreeframe(instantFrame)
            
    def delete(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            path = selected_items[0].data(1, Qt.DisplayRole)
            path = joinpath(self.root_path, path)
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
                instantFrame = self.getTreeFrame()
                if os.path.isdir(path):
                    os.removedirs(path)
                    self.labelStatus.showMessage("Folder deleted", 2000)
                else:
                    os.remove(path)
                    self.labelStatus.showMessage("File deleted", 2000)
                self.setTreeframe(instantFrame)
        
        if self.mod == "Tile":
            self.drawScene(0)
        elif self.mod == "Draw":
            self.drawScene(1)
        elif self.mod == "Map":
            self.drawScene(2)
    
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
            
    def drawScene(self, index: int, resize = False):
        self.XMin, self.XMax = self.axes.get_xlim()
        self.YMin, self.YMax = self.axes.get_ylim()
        if self.sceny is not None and (self.sceny.tile, self.sceny.draw, self.sceny.map) != (None, None, None):
            if index == 0:
                if self.checkCeiling.isChecked():
                    img = reverse(self.sceny.tile.toImgSeg())
                else:
                    img = reverse(self.sceny.tile.toImg())
                name = self.sceny.tile.name
            elif index == 1:
                if self.checkCeiling.isChecked():
                    img = reverse(self.sceny.draw.toImgSeg())
                else:
                    img = reverse(self.sceny.draw.toImg())
                name = self.sceny.draw.name
            elif index == 2:
                if self.checkCeiling.isChecked():
                    img = reverse(self.sceny.map.toImgSeg())
                else:
                    img = reverse(self.sceny.map.toImg())
                name = self.sceny.map.name
            if resize:
                self.XMin = -0.5
                self.YMin = -0.5
                self.YMax = len(img) - 0.5
                self.XMax = len(img[0]) - 0.5
            IMG = np.array(img, dtype=np.uint8)
            self.axes.cla()
            self.axes.imshow(IMG, interpolation="nearest")
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
                    S = max(n, m)
                    for i in range(n):
                        for j in range(m):
                            self.axes.text((j+0.4)*e,
                                            self.YMax - (i+0.6)*e,
                                            self.sceny.map.ground.tiles[i][j],
                                            color=self.colorGrid,
                                            fontsize=12)
            else:
                self.axes.set_xticks([])
                self.axes.set_yticks([])
        else:
            self.axes.set_xticks([])
            self.axes.set_yticks([])
        self.axes.set_xlim(self.XMin, self.XMax)
        self.axes.set_ylim(self.YMin, self.YMax)
        self.canvas.draw()
        
    def selectDirectory(self):
        path_out = Path(__file__).parent.parent.joinpath('out')
        name = QFileDialog.getExistingDirectory(
            self, "Select directory", str(path_out)
        )
        if str(Path(name)) != '':
            self.root_path = joinpath("", str(Path(name)))
            self.path = str(Path(name))
            try:
                self.initTreeWidget()
            except:
                pass
    
    def test(self, i):
        return i.text()
    
    def setMenu(self):
        
        # Actions
        #folderSelect
        selectFolderAction = QAction("Select folder", self)
        instant = self.getTreeFrame()
        selectFolderAction.triggered.connect(self.selectDirectory)
        self.setTreeframe(instant)

        #save
        saveAction = QAction("Save", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.triggered.connect(self.save)
        
        #load
        loadAction = QAction("Load", self)
        
        #copy
        copyAction = QAction("Copy", self)
        copyAction.setShortcut("Ctrl+C")
        copyAction.triggered.connect(self.copyFile)
        
        #past
        pastAction = QAction("Past", self)
        pastAction.setShortcut("Ctrl+V")
        pastAction.triggered.connect(self.pastFile)
        
        #undo
        undoAction = QAction("Undo", self)
        undoAction.setShortcut("Ctrl+Z")
        undoAction.triggered.connect(self.undo)
        
        #redo
        redoAction = QAction("Redo", self)
        redoAction.setShortcut("Ctrl+Y")
        redoAction.triggered.connect(self.redo)
                
        #folder
        newFolderAction = QAction("New Folder", self)
        newFolderAction.setShortcut("Ctrl+F")
        newFolderAction.triggered.connect(self.newFolder)
        deleteFolderAction = QAction("Delete Folder", self)
        deleteFolderAction.setShortcut(QKeySequence.Delete)
        deleteFolderAction.triggered.connect(self.delete)
        
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
        
        #mod
        setDarkAction = QAction("Set to Dark Mod", self)
        setDarkAction.triggered.connect(self.enableDarkMod)
        setWhiteAction = QAction("Set to White Mod", self)
        setWhiteAction.triggered.connect(self.enableWhiteMod)
        
        #tuto
        tutoAction = QAction("Tutorial", self)
        tutoAction.triggered.connect(self.helpMenu)
        
        #info
        infoAction = QAction("Version 1.1.0", self)

        # Menu Bar
        file_menu = self.menu.addMenu("&File")
        file_menu.addAction(selectFolderAction)
        
        file_menu.addSeparator()
        file_menu.addAction(saveAction)
        file_menu.addAction(loadAction)
        file_menu.addSeparator()
        
        file_menu.addAction(newFolderAction)
        file_menu.addAction(deleteFolderAction)
        file_menu.addSeparator()
        
        file_menu.addAction(newTileAction)
        file_menu.addAction(newDrawAction)
        file_menu.addAction(newMapAction)
        file_menu.addSeparator()
        
        file_menu.addAction(copyAction)
        file_menu.addAction(pastAction)
        
        edit_menu = self.menu.addMenu("&Edit")
        edit_menu.addAction(undoAction)
        edit_menu.addAction(redoAction)
        
        settingsMenu = self.menu.addMenu("&Settings")
        settingsMenu.addAction(showGridAction)
        settingsMenu.addAction(setColorGridAction)
        settingsMenu.addSeparator()
        
        settingsMenu.addAction(setDarkAction)
        settingsMenu.addAction(setWhiteAction)
        
        help_menu = self.menu.addMenu("&Help")
        help_menu.addAction(tutoAction)
        help_menu.addAction(infoAction)
            
    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color
            self.color_label.setStyleSheet("QLabel { background-color: %s }" % color.name())
            
    def resize(self):
        if self.mod == "Draw":
            self.sceny.draw.resize()
            self.sceny.saves.append(self.sceny.draw.copy())
            self.drawScene(1, True)
        elif self.mod == "Map":
            self.sceny.map.resize()
            self.sceny.saves.append(self.sceny.map.copy())
            self.drawScene(2, True)
        
    def setTree(self) -> None:
        self.tree = Tree(self.root_path)
                
        for c in self.tree.child:
            self.complete(c, self.treeWidget)
                                        
    def complete(self, tree, Qtree):
        item = QTreeWidgetItem(Qtree, [tree.name, tree.pathFromRoot])
        if tree.child:
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
    
    def rename(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            path = joinpath(self.path, selected_item.data(1, Qt.DisplayRole))
            self.createRename(path)
    
    def createRename(self, path, warning=0):
        abspath = '/'.join(path.split('/')[:-1])
        if warning == 1:
            name, ok = QInputDialog.getText(self, "Rename", "This file or folder already existe")
        elif warning == 2:
            name, ok = QInputDialog.getText(self, "Rename", "The chossen name is not available")
        else:
            name, ok = QInputDialog.getText(self, "Rename", "Enter the new name")
        if ok:
            if '.' in name or '/' in name or name == '':
                self.createRename(path, 2)
            elif os.path.isdir(joinpath(abspath, name)):
                self.createRename(path, 1)
            else:
                instantFrame = self.getTreeFrame()
                os.rename(path, joinpath(abspath, name))
                self.labelStatus.showMessage("Folder or file renamed", 2000)
                self.setTreeframe(instantFrame)
                
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
    
    def enableWhiteMod(self):
        plt.style.use("default")
        self.setStyle(QStyleFactory.create("Fusion"))
        palette = QPalette()
        palette.setColor(QPalette.Window, Qt.white)
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.AlternateBase, Qt.white)
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, Qt.white)
        palette.setColor(QPalette.ButtonText, Qt.black)
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
            
    def helpMenu(self):
        helpMenu = HelpWindow()
        
        helpMenu.show()
        helpMenu.exec()
    
    def getImgSize(self):
        if self.sceny.tile is not None:
            img = self.sceny.tile.toImg()
            return len(img[0]) - 0.5, len(img) - 0.5
        elif self.sceny.draw is not None:
            img = self.sceny.draw.toImg()
            return len(img[0]) - 0.5, len(img) - 0.5
        elif self.sceny.map is not None:
            img = self.sceny.map.toImg()
            return len(img[0]) - 0.5, len(img) - 0.5
        else:
            return 1, 1
            
    # Tree events
    def initTreeWidget(self):
        self.treeWidget.clear()
        self.treeWidget.setColumnCount(1)
        self.setTree()
        self.treeWidget.path = self.path
        self.treeWidget.sortItems(0, Qt.AscendingOrder)
        self.treeWidget.clicked.connect(self.clickedFile)
        self.treeWidget.doubleClicked.connect(self.doubleClickedFile)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.showMenu)
        
    def getTreeFrame(self):
        instantTree = Tree(str(self.root_path))        
        
        def setExpanded(item):
            if item.isExpanded():
                instantTree.changeExpanded(item.text(1))
            for i in range(item.childCount()):
                child = item.child(i)
                setExpanded(child)
        
        root_item = self.treeWidget.invisibleRootItem()
        setExpanded(root_item)
        return instantTree
        
    def setTreeframe(self, instantTree):
        self.tree = Tree(str(self.root_path))
        Tree.merge(instantTree, self.tree)
        self.applyTreeframe()
    
    def updateFrame(self):
        self.setTreeframe(self.frame)
        self.frame = self.getTreeFrame()
    
    def resetFrame(self):
        self.frame = self.getTreeFrame()
        
    def applyTreeframe(self):
        self.treeWidget.clear()
        self.treeWidget.setColumnCount(1)
        for child in self.tree.child:
            self.complete(child, self.treeWidget)
        self.treeWidget.clicked.connect(self.clickedFile)
        self.treeWidget.doubleClicked.connect(self.doubleClickedFile)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.treeWidget.customContextMenuRequested.connect(self.showMenu)
        self.setExpanded(self.treeWidget.invisibleRootItem())
        
        #self.displayTreeWidget()
        
    def setExpanded(self, QTree):
        if QTree.text(1):
            QTree.setExpanded(self.tree.isExpanded(QTree.text(1)))
        for i in range(QTree.childCount()):
            self.setExpanded(QTree.child(i))
         
    def displayTreeWidget(self):
        def recursiveDisplay(item, indent=""):
            print(f"{indent}{item.text(1)} {item.isExpanded()}")
            for i in range(item.childCount()):
                child = item.child(i)
                recursiveDisplay(child, indent + "  ")

        root_item = self.treeWidget.invisibleRootItem()
        recursiveDisplay(root_item)
    
    def clickedFile(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            path = selected_item.data(1, Qt.DisplayRole)
            if path.split('.')[-1] == "mprt":
                self.sceny.littleTile = Tile.load(joinpath(self.root_path, path))
                self.sceny.littleDraw = None
                self.sceny.littleMap = None
                self.sceny.littlePath = path
            elif path.split('.')[-1] == "mprd":
                self.sceny.littleTile = None
                self.sceny.littleDraw = Draw.load(joinpath(self.root_path, path))
                self.sceny.littlePath = path
            elif path.split('.')[-1] == "mprp":
                self.sceny.littleTile = None
                self.sceny.littleDraw = None
                self.sceny.littleMap = Map.load(joinpath(self.root_path, path))
                self.sceny.littlePath = path
        self.drawLittle()
        
    def copyFile(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            path = selected_item.data(1, Qt.DisplayRole)
            if path.split('.')[-1] == "mprt":
                self.copy = Tile.load(joinpath(self.root_path, path))
                self.labelStatus.showMessage("copy succed", 2000)
            elif path.split('.')[-1] == "mprd":
                self.copy = Draw.load(joinpath(self.root_path, path))
                self.labelStatus.showMessage("copy succed", 2000)
            elif path.split('.')[-1] == "mprp":
                self.copy = Map.load(joinpath(self.root_path, path))
                self.labelStatus.showMessage("copy succed", 2000)
            else:
                self.labelStatus.showMessage("This is not a file: copy failed", 4000)
        else:
            self.labelStatus.showMessage("No selected file: copy failed (looser)", 4000)
    
    def pastFile(self):
        if self.copy != None:
            try:
                selected_items = self.treeWidget.selectedItems()
                if selected_items:
                    path = selected_items[0].data(1, Qt.DisplayRole)
                    if '.' in str(path):
                        path = '/'.join(str(path).split('/')[:-1])
                    name = self.copy.name
                    name += "(1)"
                    if self.copy.type == "Tile":
                        treeFrame = self.getTreeFrame()
                        newTile = self.copy.copy()
                        newTile.name = name
                        newTile.save(joinpath(self.root_path, path))
                        newPath = ''
                        for spath in str(path).split('/'):
                            if spath not in str(self.root_path).split('/'):
                                newPath += '/'+spath
                        newPath += f"/{name}.mprt"
                        self.sceny.tile = newTile.copy()
                        self.sceny.draw = None
                        self.sceny.map = None
                        self.sceny.littleTile = newTile.copy()
                        self.sceny.littleDraw = None
                        self.sceny.littleMap = None
                        self.sceny.path = newPath
                        self.sceny.littlePath = newPath
                        self.setTreeframe(treeFrame)
                        self.drawTile(False)
                    elif self.copy.type == "Draw":
                        treeFrame = self.getTreeFrame()
                        newDraw = self.copy.copy()
                        newDraw.name = name
                        newDraw.save(joinpath(self.root_path, path))
                        newPath = ''
                        for spath in str(path).split('/'):
                            if spath not in str(self.root_path).split('/'):
                                newPath += '/'+spath
                        newPath += f"/{name}.mprd"
                        self.sceny.tile = None
                        self.sceny.draw = newDraw.copy()
                        self.sceny.map = None
                        self.sceny.littleTile = None
                        self.sceny.littleDraw = newDraw.copy()
                        self.sceny.littleMap = None
                        self.sceny.path = newPath
                        self.sceny.littlePath = newPath
                        self.setTreeframe(treeFrame)
                        self.drawDraw(False)
                    else:
                        treeFrame = self.getTreeFrame()
                        newMap = self.copy.copy()
                        newMap.name = name
                        newMap.save(joinpath(self.root_path, path))
                        newPath = ''
                        for spath in str(path).split('/'):
                            if spath not in str(self.root_path).split('/'):
                                newPath += '/'+spath
                        newPath += f"/{name}.mprp"
                        self.sceny.tile = None
                        self.sceny.draw = None
                        self.sceny.map = newMap.copy()
                        self.sceny.littleTile = None
                        self.sceny.littleDraw = None
                        self.sceny.littleMap = newMap.copy()
                        self.sceny.path = newPath
                        self.sceny.littlePath = newPath
                        self.setTreeframe(treeFrame)
                        self.drawMap(False)
                else:
                    self.labelStatus.showMessage("No selected file: past failed (looser)", 4000)
            except:
                self.labelStatus.showMessage("You broke the matrix, you are the choosen one", 8000)
        else:
            self.labelStatus.showMessage("No copied file: past failed", 4000)
        
    def showMenu(self, position):
        item = self.treeWidget.itemAt(position)
        
        if item is not None:
            self.treeWidget.clearSelection()
            item.setSelected(True)
            path = item.data(1, Qt.DisplayRole)
            if self.sceny.path == None or not '.' in self.sceny.path:
                if self.sceny.littlePath == None:
                    self.sceny.littlePath = path
            
            self.menu = QMenu()
            
            #Copy
            copyAction = QAction("Copy", self)
            copyAction.triggered.connect(self.copyFile)
            
            #Past
            pastAction = QAction("Past", self)
            pastAction.triggered.connect(self.pastFile)
            
            #Rename
            renameAction = QAction("Rename", self)
            renameAction.triggered.connect(self.rename)
            
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
            
            self.menu.addAction(copyAction)
            self.menu.addAction(pastAction)
            self.menu.addAction(renameAction)
            self.menu.addSeparator()
            self.menu.addAction(newFolderAction)
            self.menu.addAction(newTileAction)
            self.menu.addAction(newDrawAction)
            self.menu.addAction(newMapAction)
            self.menu.addSeparator()
            self.menu.addAction(deletAction)
                        
            self.menu.popup(QCursor.pos())
    
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
    def updateAction(self, action):
        if action.text() in {"Zoom", "Pan"}:
            if self.action == action.text():
                self.action = None
            else:
                self.action = action.text()
    
    def mousePressEvent(self, event):
        self.XMin, self.XMax = self.axes.get_xlim()
        self.YMin, self.YMax = self.axes.get_ylim()
        if event.inaxes is not None and self.action is None:
            X, Y = self.getImgSize()
            x, y = int(Y - event.ydata), int(event.xdata + 0.5)
            x, y = int(x), int(y+0.5)
            self.dragPos = [(x, y)]
            if self.sceny.tile != None and self.checkCeiling.isChecked():
                self.sceny.tile.changeCeiling((x, y))
                self.drawScene(0)
            elif event.button == 1: # left click
                self.change(x, y)
            elif event.button == 3: # right click
                if self.sceny.draw != None:
                    self.sceny.draw.setTile((int(x/N), int(y/N)), None)
                    self.sceny.saves.append(self.sceny.draw.copy())
                    self.drawScene(1)
                elif self.sceny.map != None:
                    self.sceny.map.setTile((int(x/N), int(y/N)), None)
                    self.sceny.saves.append(self.sceny.map.copy())
                    self.drawScene(2)
    
    def on_mouse_move(self, event):
        if self.mod == "Tile" and self.action is None and self.checkDrag.isChecked() and event.button==1 and event.xdata is not None and event.ydata is not None:
            X, Y = self.getImgSize()
            x, y = int(Y - event.ydata), int(event.xdata + 0.5)
            x, y = int(x), int(y+0.5)
            if self.checkCeiling.isChecked():
                self.dragPos.append((x, y))
                if self.dragPos[-1] != self.dragPos[-2]:
                    self.sceny.tile.changeCeiling((x, y))
                    self.drawScene(0)
            else:
                if not (x, y) in self.dragPos:
                    self.dragPos.append((x, y))
                    self.change(x, y)
    
    def change(self, x: int , y: int):
        try:
            if self.mod == "Tile":
                self.current_color
        except:
            return
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
            
    def mouseReleaseEvent(self, event):
        self.dragPos = []
        self.dragIter = 0
                            
    def doubleClickedFile(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            path = selected_item.data(1, Qt.DisplayRole)
            if path.split('.')[-1] == "mprt":
                tile = Tile.load(joinpath(self.root_path, path))
                changed = True
                i = 1048576
                if self.mod == "Tile":
                    changed = False
                    if self.sceny.path != None and tile != self.sceny.tile and self.sceny.tile != Tile.load(joinpath(self.root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Draw":
                    if self.sceny.path != None and self.sceny.draw != Draw.load(joinpath(self.root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Map":
                    if self.sceny.path != None and self.sceny.map != Map.load(joinpath(self.root_path, self.sceny.path)):
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
                    self.sceny.littleTile = Tile.load(joinpath(self.root_path, path))
                    self.sceny.littleDraw = None
                    self.sceny.path = path
                    self.sceny.saves.init()
                    self.sceny.saves.append(self.sceny.tile.copy())
                    self.drawLittle()
                    if self.mod != "Tile":
                        self.drawTile(False, True)
                    self.drawScene(0, True)
                    
            elif path.split('.')[-1] == "mprd":
                draw = Draw.load(joinpath(self.root_path, path))
                i = 1048576
                changed = True
                if self.mod == "Tile":
                    if self.sceny.path != None and self.sceny.tile != Tile.load(joinpath(self.root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Draw":
                    changed = False
                    if self.sceny.path != None and draw != self.sceny.draw and self.sceny.draw != Draw.load(joinpath(self.root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Map":
                    if self.sceny.path != None and self.sceny.map != Map.load(joinpath(self.root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                if i == 1048576: # Button for 'ignore'... 
                    self.sceny.draw = draw.copy()
                    self.sceny.tile = None 
                    self.sceny.map = None
                    self.sceny.littleDraw = Draw.load(joinpath(self.root_path, path))
                    self.sceny.littleTile = None
                    self.sceny.littleMap = None
                    self.sceny.path = path
                    self.sceny.saves.init()
                    self.sceny.saves.append(self.sceny.draw.copy())
                    self.drawLittle()
                    if self.mod != "Draw":
                        self.drawDraw(False, True)
                    self.drawScene(1, True)
                            
            elif path.split('.')[-1] == "mprp":
                map_ = Map.load(joinpath(self.root_path, path))
                i = 1048576
                changed = True
                if self.mod == "Tile":
                    if self.sceny.path != None and self.sceny.tile != Tile.load(joinpath(self.root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Draw":
                    if self.sceny.path != None and self.sceny.draw != Draw.load(joinpath(self.root_path, self.sceny.path)):
                        msg = QMessageBox()
                        msg.setWindowTitle("Alert")
                        msg.setText("You didn't save your work !")
                        msg.setIcon(QMessageBox.Warning)
                        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ignore)
                        msg.buttonClicked.connect(self.test)
                        i = msg.exec()
                elif self.mod == "Map":
                    changed = False
                    if self.sceny.path != None and map_ != self.sceny.map and self.sceny.map != Map.load(joinpath(self.root_path, self.sceny.path)):
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
                    self.sceny.littleMap = Map.load(joinpath(self.root_path, path))
                    self.sceny.path = path
                    self.sceny.saves.init()
                    self.sceny.saves.append(self.sceny.map.copy())
                    self.drawLittle()
                    if self.mod != "Map":
                        self.drawMap(False, True)
                    self.drawScene(2, True)
                    
    
    def checkChange(self, box: int=0):
        if len([value for value in [self.replaceCheck.isChecked(), self.paintBucketCheck.isChecked(), self.superPaintBucketCheck.isChecked()] if value]) > 1:
            if box == 0:
                self.paintBucketCheck.setChecked(False)
                self.superPaintBucketCheck.setChecked(False)
            elif box == 1:
                self.replaceCheck.setChecked(False)
                self.superPaintBucketCheck.setChecked(False)
            else:
                self.replaceCheck.setChecked(False)
                self.paintBucketCheck.setChecked(False)


            
if __name__=="__main__":
    app = QApplication(sys.argv)
    
    ex = MainWindow()
    
    ex.show()
    sys.exit(app.exec())
