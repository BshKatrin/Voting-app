# Pas d'interet d'utiliser ce fichier

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)
import sys
from votingSystem import VoteSystemWindow


class GraphRandomWindow(QWidget):
    def __init__(self):
        super().__init__()

        # creation des bouton
        button_result = QPushButton("Voting results")
        button_result.setFixedSize(150, 30)
        button_result.clicked.connect(self.resultButtonClicked)
        button_home = QPushButton("Home")
        button_home.setFixedSize(100, 25)
        button_home.clicked.connect(self.homeButtonClicked)

        # def du layout
        layout = QVBoxLayout()
        layout.addWidget(button_result)

        # Creation du widget central et affectation du layout
        centralWidget = QWidget(self)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        # Creation du status bar et mise du bouton
        status_bar = self.statusBar()
        status_bar.addWidget(button_home)

    def resultButtonClicked(self):
        pass
        # voteWindow=VoteSystemWindow(app)
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
