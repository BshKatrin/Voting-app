from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .widget_map import WidgetMap
from .widget_results import WidgetResults

from electoral_systems import Election


class HomeWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.election = Election()

        # Set main_window size
        screen_size = app.primaryScreen().geometry()
        size_size = min(screen_size.height(), screen_size.width())
        self.setGeometry(screen_size.x(), screen_size.y(), size_size, size_size)
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
        # self.election.create_electors()
        self.election.calculate_prop_satisfation()
        # self.election.make_delegations()

        # Delete widget with map
        self.widget_map.sig_widget_map_destroying.emit()
        self.widget_map.deleteLater()
        # Delete checkbox
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
            self.widgetResults.sig_widget_results_destroying.emit()
            self.widgetResults.deleteLater()
