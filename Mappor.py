from code.viewer import *
import sys

if __name__=="__main__":
    app = QApplication(sys.argv)
    
    ex = MainWindow()
    
    ex.show()
    sys.exit(app.exec())