# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import FourierTransformApp

def main():
    app = QApplication(sys.argv)
    main_window = FourierTransformApp()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()