from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QApplication,
    QLineEdit,
)
import sys

from .settings import MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT
from .graph_random import GraphRandom
from .voting_checkbox import VotingCheckbox


from electoral_systems import Election
from electoral_systems.voting_rules import constants


class HomeWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.election = Election()

        # dimension et titre de la fenetre (posX,posY,tailleX,tailleY)
        self.setGeometry(0, 0, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.setWindowTitle("Voting app")

        # Central Widget, layout (vertical)
        self.main_widget = QWidget(parent=self)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.initUIHome()

        # Navigation buttons
        self.button_home = QPushButton("Home")
        self.button_home.clicked.connect(self.backHomeWindow)
        self.button_vote = QPushButton("Vote")
        self.button_vote.clicked.connect(self.startElection)

    def initUIHome(self):
        # Buttons graph
        self.btn_random = QPushButton("Random")
        # self.btn_random.setFixedSize(150, 30)
        self.layout.addWidget(self.btn_random)
        self.btn_random.clicked.connect(self.showRandomGraph)
        # self.btn_manual = QPushButton("Manual")
        # self.btn_manual.setFixedSize(150, 30)
        # self.layout.addWidget(self.btn_manual)
        # self.btn_manual.clicked.connect(self.showManualGraph)

    def initUIGraph(self):
        self.cleanWindow()
        self.layout.addWidget(self.button_home)
        self.layout.addWidget(self.button_vote)

    def showRandomGraph(self):
        self.initUIGraph()
        self.graph_random = GraphRandom(parent=self)
        self.layout.addWidget(self.graph_random)

    def startElection(self):
        self.voteSelectionWidget = VotingCheckbox()
        print(len(self.election.candidates))
        self.voteSelectionWidget.desactivate_checkboxes()
        self.layout = QVBoxLayout()
        self.voteSelectionWidget.show()
        print(self.election.__dict__)

    # delete all widgets from main_layout
    def cleanWindow(self):
        for i in reversed(range(self.layout.count())):
            widgetToRemove = self.layout.itemAt(i).widget()
            # remove it from the layout list
            self.layout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

    def backHomeWindow(self):
        self.cleanWindow()
        self.initUIHome()

    def quit_app(self):
        self.app.quit()


if __name__ == "__main__":
    app = QApplication()
    window = HomeWindow(sys.argv)
    window.show()
    sys.exit(app.exec())
