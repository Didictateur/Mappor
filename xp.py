import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QColorDialog, QTreeWidget, QTreeWidgetItem, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QBrush
from PyQt5.QtCore import Qt, QFile, QIODevice

class PixelEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialisation de l'interface utilisateur
        self.setWindowTitle("Editeur de Map Pixel Art")
        self.setGeometry(100, 100, 800, 600)

        # Zone de travail pour dessiner des pixels
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setSceneRect(0, 0, 400, 400)

        # Palette de couleurs
        self.color_label = QLabel("Couleur sélectionnée : ")
        self.color_button = QPushButton("Sélectionner une couleur")
        self.color_button.clicked.connect(self.select_color)

        # Boutons pour ouvrir et enregistrer des maps
        self.open_button = QPushButton("Ouvrir")
        self.open_button.clicked.connect(self.open_map)
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save_map)

        # Arbre des dossiers contenant des projets
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Projets")

        # Mise en page
        layout = QHBoxLayout()
        layout.addWidget(self.view)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.color_label)
        right_layout.addWidget(self.color_button)
        right_layout.addWidget(self.open_button)
        right_layout.addWidget(self.save_button)
        right_layout.addWidget(self.tree_widget)

        layout.addLayout(right_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Variables de l'éditeur de map
        self.current_color = Qt.black

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color
            self.color_label.setStyleSheet("QLabel { background-color: %s }" % color.name())

    def open_map(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir une map", "", "Fichiers de map (*.map)")
        if file_path:
            with QFile(file_path) as file:
                if file.open(QIODevice.ReadOnly):
                    pixmap = QPixmap()
                    pixmap.loadFromData(file.readAll())
                    self.scene.clear()
                    self.scene.addPixmap(pixmap)

    def save_map(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer la map", "", "Fichiers de map (*.map)")
        if file_path:
            with QFile(file_path) as file:
                if file.open(QIODevice.WriteOnly):
                    self.scene.clearSelection()
                    pixmap = self.scene.renderToPixmap()
                    pixmap.save(file, "PNG")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            scene_pos = self.view.mapToScene(pos)
            rect = QGraphicsRectItem(scene_pos.x(), scene_pos.y(), 1, 1)
            rect.setPen(QPen(Qt.NoPen))
            rect.setBrush(QBrush(self.current_color))
            self.scene.addItem(rect)

        elif event.button() == Qt.RightButton:
            pos = event.pos()
            scene_pos = self.view.mapToScene(pos)
            items = self.scene.items(scene_pos)
            if items:
                self.scene.removeItem(items[0])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = PixelEditor()
    editor.show()
    sys.exit(app.exec_())
