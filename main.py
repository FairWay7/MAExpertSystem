import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

# from ui.main_window import MainWindow
from ui.main_window import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Установка стиля
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()