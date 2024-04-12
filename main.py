from sys import argv, exit

from PySide6.QtWidgets import QApplication
from graphics.home_window import HomeWindow

if __name__ == "__main__":
    app = QApplication(argv)
    app.setStyle("Fusion")

    window = HomeWindow(app)

    window.show()
    exit(app.exec())

