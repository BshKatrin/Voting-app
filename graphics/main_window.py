from functools import partial

from PySide6.QtCore import Qt, Slot, QObject, Signal
from PySide6.QtGui import QAction
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
    QFileDialog,
)

from .widget_map import WidgetMap
from .widget_results import WidgetResults

from electoral_systems import Election

from sqlite import ImportData, ExportData
import sqlite3


class HomeWindow(QMainWindow):
    # Signal to indicate that data import (resp. export) was succesful
    # Bool indicated if with or without results
    sig_data_imported = Signal(bool)
    sig_data_exported = Signal(bool)

    # Signal to indicate that widgetmap if ON (resp. OFF)
    sig_widget_map_on = Signal(bool)

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.election = Election()

        self.setScreenGeometry()

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

        self.sig_data_imported.connect(self.switchWidgetImport)

        self.createActions()
        self.createMenus()
        self.initUIHome()

    # Set main_window size
    def setScreenGeometry(self):
        # Find center
        x = self.app.primaryScreen().availableGeometry().x()
        screen_size = self.app.primaryScreen().availableSize()
        center_x = screen_size.width() / 2 + x

        # Determine main_window one side size
        side_size = min(screen_size.height(), screen_size.width())
        self.setGeometry(center_x - side_size / 2, 0, side_size, side_size)

    # With results : MainWindow, WidgetResults only
    # No results : MainWindow, WidgetMap only
    @Slot(bool)
    def importData(self, with_results):
        db_file_name = QFileDialog.getOpenFileName(
            self, "Choose database", "", "SQLite databases : (*.db)"
        )

        # Do nothing if no file was chosen
        if not db_file_name[0]:
            return

        connection = sqlite3.connect(db_file_name[0])

        success, msg = ImportData.import_people(connection, with_results)

        connection.close()

        if success:
            self.sig_data_imported.emit(with_results)
        else:
            # Add a pop up in that case with return msg
            print(msg)

    @Slot(bool)
    def exportData(self, with_results):
        db_file_name = QFileDialog.getSaveFileName(
            self, "Save database", "", "SQLite databases : (*.db)"
        )

        # Do nothing if no file was chosen
        if not db_file_name[0]:
            return

        connection = sqlite3.connect(db_file_name[0])
        ExportData.create_database_people(connection)

        if with_results:
            ExportData.create_database_results(connection)

        connection.close()
        self.sig_data_exported.emit(with_results)

    @Slot()
    def switchWidgetImport(self, with_results):
        self.cleanWindow()
        if not with_results:
            self.initUIMap(True)
            return

        self.election.calculate_prop_satisfation()
        # For polls
        self.election.define_ranking()
        self.election.calculate_results(imported=True)
        self.initUIResults()

    def createActions(self):
        # Import
        self.import_with_results = QAction("Import with results", self)
        self.import_no_results = QAction("Import without results", self)

        self.import_with_results.triggered.connect(lambda: self.importData(True))
        self.import_no_results.triggered.connect(lambda: self.importData(False))

        # Export
        self.export_with_results = QAction("Export with results", self)
        self.export_no_results = QAction("Export without results", self)

        self.export_with_results.triggered.connect(lambda: self.exportData(True))
        self.export_no_results.triggered.connect(lambda: self.exportData(False))

    def createMenus(self):
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        file_menu = menu_bar.addMenu(QObject.tr("&File"))

        import_menu = file_menu.addMenu(QObject.tr("&Import"))
        import_menu.addAction(self.import_with_results)
        import_menu.addAction(self.import_no_results)

        export_menu = file_menu.addMenu(QObject.tr("&Export"))
        export_menu.addAction(self.export_with_results)
        export_menu.addAction(self.export_no_results)

    def toggleIEOptions(self, type, with_results_status, no_results_status):
        match type:
            case ImportData.IMPORT:
                self.import_with_results.setEnabled(with_results_status)
                self.import_no_results.setEnabled(no_results_status)
            case ExportData.EXPORT:
                self.export_with_results.setEnabled(with_results_status)
                self.export_no_results.setEnabled(no_results_status)

    def initNavigation(self):
        self.button_home = QPushButton("Home", parent=self)
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

        quit_btn = QPushButton("Quit", parent=self.main_widget)
        quit_btn.setFixedSize(self.width() * 0.3, 30)
        quit_btn.clicked.connect(self.quit_app)
        # Toggle import, export
        self.toggleIEOptions(ExportData.EXPORT, False, False)
        self.toggleIEOptions(ImportData.IMPORT, True, True)

        layout.addWidget(
            self.start,
            alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter,
        )
        layout.addWidget(
            settings_btn,
            alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter,
        )

        layout.addWidget(
            quit_btn,
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

    @Slot()
    def initUIMap(self, imported=False):
        self.cleanWindow()

        self.initNavigation()

        self.toggleIEOptions(ExportData.EXPORT, False, True)
        self.toggleIEOptions(ImportData.IMPORT, False, True)

        self.widget_map = WidgetMap(imported, parent=self)
        self.widget_map.sig_start_election.connect(self.startElection)
        self.layout.addWidget(self.widget_map)

    @Slot()
    def initUIResults(self):
        self.toggleIEOptions(ExportData.EXPORT, True, True)
        self.toggleIEOptions(ImportData.IMPORT, False, False)

        self.widgetResults = WidgetResults(self.main_widget)
        self.layout.addWidget(self.widgetResults, alignment=Qt.AlignTop)

    @Slot(list)
    def startElection(self, constantsList):
        # Add keys to results dict in Election
        self.election.init_results_keys(constantsList)
        self.election.set_average_electors_position()
        self.election.calculate_prop_satisfation()
        # self.election.make_delegations() -> WidgetMap

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
        self.quit_app()

    @Slot()
    def quit_app(self):
        self.app.quit()
