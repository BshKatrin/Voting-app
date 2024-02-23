from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .settings import MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT

from .widget_map import WidgetMap

from .widget_results import WidgetResults

from electoral_systems import Election


class HomeWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.election = Election()

        # dimension et titre de la fenetre (posX,posY,tailleX,tailleY)
        self.setGeometry(0, 0, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.setWindowTitle("Voting app")

        # Main widget, layout
        self.main_widget = QWidget(parent=self)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Widgets
        self.voteSelectionWidget = None
        self.widgetResults = None
        self.widgetMap = None

        self.initUIHome()

    def initNavigation(self):
        self.button_home = QPushButton("Home", parent=self.main_widget)
        self.button_home.clicked.connect(self.backHomeWindow)
        self.layout.addWidget(self.button_home)

    def initUIHome(self):
        self.start = QPushButton("Start", parent=self.main_widget)
        self.start.setFixedSize(self.width() * 0.3, 30)
        self.start.clicked.connect(self.initUIMap)
        self.layout.addWidget(
            self.start, Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignHCenter
        )

    def initUIMap(self):
        self.cleanWindow()

        self.initNavigation()

        self.widget_map = WidgetMap(parent=self)
        self.widget_map.sig_start_election.connect(self.startElection)
        self.layout.addWidget(self.widget_map)

    def initUIResults(self):
        self.widgetResults = WidgetResults(self.main_widget)
        self.layout.addWidget(self.widgetResults, alignment=Qt.AlignTop)

    @Slot(list)
    def startElection(self, constantsList):
        # Add keys to results dict in Election
        self.election.init_results_keys(constantsList)
        # Crate all creators from stored positions
        self.election.create_electors()
        # Delete widget with map
        self.widget_map.deleteLater()
        # Delete checkbox
        self.widget_map.voting_rules_checkbox.deleteLater()
        # Initialize Results page (winners, results, graphs)
        self.initUIResults()

    # delete all widgets from main_layout
    @Slot()
    def cleanWindow(self):
        for i in reversed(range(self.layout.count())):
            widgetToRemove = self.layout.itemAt(i).widget()
            widgetToRemove.deleteLater()

    @Slot()
    def backHomeWindow(self):
        self.cleanWindow()
        self.initUIHome()
        self.election.delete_all_data()

        if self.widgetResults:
            self.widgetResults.deleteLater()
