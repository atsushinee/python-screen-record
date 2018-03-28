# _*_ coding:utf-8 _*_
import sys

from PyQt5.QtWidgets import QApplication

from app import ScreenBar

if __name__ == '__main__':
    app = QApplication(sys.argv)
    bar = ScreenBar()

    bar.show()
    sys.exit(app.exec_())