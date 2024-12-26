import sys
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QMainWindow, QMenu
from PyQt6.QtGui import QIcon, QAction


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initGUI()

    def initGUI(self):
        # status
        self.statusBar().showMessage('Ready')

        # menu
        menubar = self.menuBar()
        # macos needs this command to make menubar work!
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('&File')

        exitAct = QAction('&Exit', self)
        exitAct.triggered.connect(self.close)

        impMenu = QMenu('Import', self)
        impAct = QAction('Import mail', self)
        impMenu.addAction(impAct)

        newAct = QAction('New', self)

        fileMenu.addAction(newAct)
        fileMenu.addMenu(impMenu)

        self.setGeometry(500, 300, 500, 300)
        self.setWindowTitle("test for statusbar")
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
