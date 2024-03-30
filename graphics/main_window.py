from functools import partial

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QSpinBox,
    QLabel,
    QCheckBox,
    QGridLayout,
    QSizePolicy,
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
        # screen_size = app.primaryScreen().availableGeometry()
        screen_size = app.primaryScreen().availableSize()
        side_size = min(screen_size.height(), screen_size.width())
        # self.setGeometry(screen_size.x(), screen_size.y(), side_size, side_size)
        self.setGeometry(0, 0, side_size, side_size)
        self.setWindowTitle("Voting app")

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # Main widget, layout
        self.main_widget = QWidget(parent=self)
        self.layout = QVBoxLayout()

        self.main_widget.setLayout(self.layout)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(self.main_widget)

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
        widget_btns = QWidget(parent=self.main_widget)

        layout = QVBoxLayout()
        layout.setSpacing(30)
        widget_btns.setLayout(layout)

        self.start = QPushButton("Start", parent=self.main_widget)
        self.start.setFixedSize(self.width() * 0.3, 30)
        self.start.clicked.connect(self.initUIMap)

        settings_btn = QPushButton("Settings", parent=self.main_widget)
        settings_btn.setFixedSize(self.width() * 0.3, 30)
        settings_btn.clicked.connect(self.initSettings)

        layout.addWidget(
            self.start,
            alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter,
        )
        layout.addWidget(
            settings_btn,
            alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter,
        )

        self.layout.addWidget(
            widget_btns,
            alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter,
        )

    @Slot()
    def initSettings(self):
        self.cleanWindow()
        # Widget for settings
        settings_widget = QWidget(self.main_widget)
        # settings_widget.setStyleSheet("background-color : white")
        settings_layout = QGridLayout()
        settings_layout.setSpacing(40)
        settings_widget.setLayout(settings_layout)
        self.layout.addWidget(
            settings_widget,
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
        )

        # Number of polls
        polls_label = QLabel(parent=settings_widget)
        polls_label.setText("Number of polls to conduct")
        nb_polls_btn = QSpinBox(parent=settings_widget)

        # Limits
        nb_polls_btn.setMinimum(0)
        nb_polls_btn.setMaximum(10)
        nb_polls_btn.setValue(self.election.nb_polls)
        nb_polls_btn.valueChanged.connect(self.setNumberPolls)

        # Activate liquid democracy checkbox
        liquid_democracy_label = QLabel(parent=settings_widget)
        liquid_democracy_label.setText("Activate liquid democracy")
        liquid_democracy_checkbox = QCheckBox(parent=settings_widget)
        liquid_democracy_checkbox.setChecked(self.election.liquid_democracy_activated)
        liquid_democracy_checkbox.stateChanged.connect(self.toggleLiquidDemocracy)

        # Save button, go back on main window
        save_button = QPushButton("Save", parent=settings_widget)
        save_button.clicked.connect(self.saveSettings)
        save_button.setFixedHeight(30)

        # Add to grid layout (rows = 3 x cols = 3)
        # Polls
        settings_layout.addWidget(polls_label, 0, 0, 1, 2)
        settings_layout.addWidget(nb_polls_btn, 0, 2, 1, 1)
        # Liquid democracy
        settings_layout.addWidget(liquid_democracy_label, 1, 0, 1, 2)
        settings_layout.addWidget(
            liquid_democracy_checkbox, 1, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignRight
        )
        # Save button
        settings_layout.addWidget(save_button, 2, 0, 1, 3)

    @Slot()
    def saveSettings(self):
        self.cleanWindow()
        self.initUIHome()

    @Slot(int)
    def setNumberPolls(self, nb_polls):
        self.election.nb_polls = nb_polls

    @Slot(int)
    def toggleLiquidDemocracy(self, state):
        self.election.liquid_democracy_activated = bool(state)

    def initUIMap(self):
        self.cleanWindow()
        print(self.election.liquid_democracy_activated)

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
        self.election.calculate_results()
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
        self.election.set_default_settings()

        if self.widgetResults:
            self.widgetResults.sig_widget_results_destroying.emit()
            self.widgetResults.deleteLater()

    def closeEvent(self, event):
        self.app.quit()
