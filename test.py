from code.viewer import *


# t = Tile(4)
# t.setPixel((0, 0), [255, 255, 255])
# t.setPixel((1, 1), [255, 255, 255])
# t.setPixel((2, 2), [255, 255, 255])
# t.setPixel((3, 3), [255, 255, 255])
# t.setPixel((0, 1), [255, 0, 255])

# t.save("./saves/tile")
# nt = Tile.load("./saves/tile/0.mprt")

# d = Draw((2, 2), 4)
# d.draw = [[t, t], [t, None]]
# d.save("./saves/draw")



if __name__=="__main__":
    app = QApplication(sys.argv)
    
    ex = MainWindow()
    
    ex.show()
    sys.exit(app.exec())