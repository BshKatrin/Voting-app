from PySide6.QtWidgets import QApplication
import sys

from graphics.main_window import HomeWindow

if __name__ == "__main__":
    app = QApplication([])
    window = HomeWindow(app)

    window.show()
    sys.exit(app.exec())
