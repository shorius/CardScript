# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import CardScript

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CardScript.MainWindow()
    window.show()
    sys.exit(app.exec_())
