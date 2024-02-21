from PySide6.QtWidgets import QApplication, QStyleFactory

import sys

from graphics.main_window import HomeWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = HomeWindow(app)

    window.show()
    sys.exit(app.exec())
