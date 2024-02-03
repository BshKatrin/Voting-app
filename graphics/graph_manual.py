from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)

# from .votingSystem import VoteSystemWindow
# from graphics import Graph
import sys
from .graph import Graph


class GraphManualWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # creation des bouton
        self.button_result = QPushButton("Voting results")
        self.button_result.setFixedSize(150, 30)
        self.button_result.clicked.connect(self.resultButtonClicked)
        self.button_home = QPushButton("Home")
        self.button_home.setFixedSize(100, 25)
        self.button_home.clicked.connect(self.homeButtonClicked)
        # creation du widget du graphe
        # graph = Graph()

        # def du layout en grille (ligne,colone)
        self.layout = QGridLayout()
        # layout.addWidget(graph, 0, 0)
        self.layout.addWidget(self.button_result, 1, 0)
        self.layout.addWidget(self.button_home, 0, 0)
        # Creation du widget central et affectation du layout
        # centralWidget = QWidget(self)
        # centralWidget.setLayout(layout)
        # self.setCentralWidget(centralWidget)

        # Creation du status bar et mise du bouton
        # status_bar = self.statusBar()
        # status_bar.addWidget(button_home)

    def resultButtonClicked(self):
        pass
        # voteWindow = VoteSystemWindow(app)
        # self.close()
        # voteWindow.show()
        # sys.exit(app.exec())

    def homeButtonClicked(self):
        pass
        # from main_window import HomeWindow

        # homeWindow = HomeWindow(app)
        # self.close()
        # homeWindow.show()
        # sys.exit(app.exec())
