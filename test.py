import sys

from code.help import *

if __name__=="__main__":
    app = QApplication(sys.argv)
    
    ex = HelpWindow()
    
    ex.show()
    sys.exit(app.exec())