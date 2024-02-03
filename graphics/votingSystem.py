from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)
import sys


class VoteSystemWindow(QWidget):
    def __init__(self, app):
        super().__init__()

        # def des bouttons
        button_home = QPushButton("Home")
        button_home.setFixedSize(100, 25)
        button_home.clicked.connect(self.homeButtonClicked)
        button_back = QPushButton("Back")
        button_back.setFixedSize(100, 25)
        button_back.clicked.connect(self.backButtonClicked)

        # Creation du status bar et mise du bouton
        status_bar = self.statusBar()
        status_bar.addWidget(button_home)

    def homeButtonClicked(self):
        pass
        # from main_window import HomeWindow

        # homeWindow = HomeWindow(app)
        # self.close()
        # homeWindow.show()
        # sys.exit(app.exec())

    def backButtonClicked(self):
        pass
        # from graph_random import GraphRandomWindow

        # graphWindow = GraphRandomWindow(app)
        # self.close()
        # graphWindow.show()
