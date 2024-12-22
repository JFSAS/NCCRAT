import sys
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QApplication, QWidget, QToolTip, QPushButton
from PyQt6.QtGui import QFont


class Zj(QWidget): 
    def __init__(self):
        super().__init__() # call father's init func
        self.initUI()
        
    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('This is a <b>QWidget</b> widget.')
        
        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget.')
        
        btn.resize(btn.sizeHint())
        btn.move(50, 50)
        
        self.setGeometry(300,300,300,200)
        self.setWindowTitle('Tooltips')
        self.show()
    

def main():
    app = QApplication(sys.argv)
    zj = Zj()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
