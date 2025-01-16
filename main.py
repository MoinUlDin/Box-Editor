from Local_Scripts.main_window import MainWindow
from PyQt6.QtWidgets import QApplication
import sys

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())