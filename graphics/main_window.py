from PySide6.QtCore import QSize, Qt
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
from .widget_results import WidgetResults

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

        # Disable button by default
        self.button_vote = QPushButton("Vote")
        self.button_vote.setEnabled(False)
        self.button_vote.clicked.connect(self.startElection)

        # Button to activate checkbox
        self.button_choose = QPushButton("Choose voting rules")
        self.button_choose.clicked.connect(self.chooseVotingRules)

    def initUIHome(self):
        # Buttons graph
        self.btn_random = QPushButton("Random")
        # self.btn_random.setFixedSize(150, 30)
        self.layout.addWidget(self.btn_random)
        self.btn_random.clicked.connect(self.showRandomGraph)

    def initUIGraph(self):
        self.cleanWindow()
        self.layout.addWidget(self.button_home)
        self.layout.addWidget(self.button_vote)
        self.layout.addWidget(self.button_choose)

    def initUIResults(self):
        self.cleanWindow()
        self.layout.addWidget(self.button_home)
        self.widgetResults = WidgetResults(self.main_widget)
        self.layout.addWidget(self.widgetResults, alignment=Qt.AlignTop)

    # Button handler
    def showRandomGraph(self):
        self.initUIGraph()
        self.graph_random = GraphRandom(parent=self)
        self.layout.addWidget(self.graph_random)

    def chooseVotingRules(self):
        # Show checkbox
        self.voteSelectionWidget = VotingCheckbox(parent=None, main_window=self)
        # Desactivate certain checkboxes based on nb of candidates
        self.voteSelectionWidget.desactivateCheckboxes()
        self.voteSelectionWidget.show()

    def startElection(self):
        # Add keys to a results in Election
        self.election.init_results_keys(self.voteSelectionWidget.getConstantsSet())
        # Delete widget checkbox completely
        self.voteSelectionWidget.destroy(destroyWindow=True)
        self.initUIResults()

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
        self.election.delete_all_data()

    def quitApp(self):
        self.app.quit()


if __name__ == "__main__":
    app = QApplication()
    window = HomeWindow(sys.argv)
    window.show()
    sys.exit(app.exec())
