import sqlite3

from PySide6.QtCore import Qt, Slot, QObject, Signal, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
)

from .home_window_utls import SettingsWidget
from .widget_map import WidgetMap
from .widget_results import WidgetResults

from electoral_systems import Election

from sqlite import ImportData, ExportData


class HomeWindow(QMainWindow):
    # Signal to indicate that data import was succesful
    # Bool indicated if with or without results
    sig_data_imported = Signal(bool)

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
        side_size = min(screen_size.height(), screen_size.width()) * 0.9
        self.setGeometry(center_x - side_size / 2, 0, side_size, side_size)

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

    @Slot(str)
    def showPopupMsg(self, msg):
        popup = QMessageBox(parent=self.main_widget)
        popup.setIcon(QMessageBox.Icon.Warning)
        popup.setText(msg)
        popup.addButton(QMessageBox.StandardButton.Close)
        # auto-close of a popup after 2 sec
        timer_close = QTimer()
        timer_close.singleShot(2000, popup, popup.close)
        popup.exec()

    # With results : MainWindow, WidgetsResults only
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
            self.showPopupMsg(msg)

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

    def toggleIEOptions(self, type, with_results_status, no_results_status):
        if type == ImportData.IMPORT:
            self.import_with_results.setEnabled(with_results_status)
            self.import_no_results.setEnabled(no_results_status)
        if type == ExportData.EXPORT:
            self.export_with_results.setEnabled(with_results_status)
            self.export_no_results.setEnabled(no_results_status)

    @Slot()
    def switchWidgetImport(self, with_results):
        self.cleanWindow()
        if not with_results:
            self.initUIMap()
            return

        self.election.start_election(imported=True)
        self.initUIResults()

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
        settings_btn.clicked.connect(self.initUISettings)

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
    def initUISettings(self):
        self.cleanWindow()
        settings_widget = SettingsWidget(self)
        self.layout.addWidget(
            settings_widget,
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
        )
        settings_widget.sig_saved.connect(self.saveSettings)

    @Slot()
    def saveSettings(self):
        self.cleanWindow()
        self.initUIHome()

    @Slot()
    def initUIMap(self):
        self.cleanWindow()

        self.initNavigation()

        self.toggleIEOptions(ExportData.EXPORT, False, True)
        self.toggleIEOptions(ImportData.IMPORT, False, True)

        self.widget_map = WidgetMap(parent=self)
        self.widget_map.sig_start_election.connect(self.startElection)
        self.layout.addWidget(self.widget_map)

    @Slot()
    def initUIResults(self):
        self.cleanWindow()

        self.initNavigation()
        self.toggleIEOptions(ExportData.EXPORT, True, True)
        self.toggleIEOptions(ImportData.IMPORT, False, False)

        self.widgetResults = WidgetResults(self.main_widget)
        self.layout.addWidget(self.widgetResults, alignment=Qt.AlignTop)

    @Slot(list)
    def startElection(self, constantsList):
        # Delete widget with map
        self.widget_map.sig_widget_map_destroying.emit()
        self.widget_map.deleteLater()

        self.election.start_election(chosen_voting_rules=constantsList)

        # Initialize Results page (winners, results, graphs)
        self.initUIResults()

    @Slot()
    def backHomeWindow(self):
        self.cleanWindow()
        self.initUIHome()

        self.election.delete_all_data()
        self.election.set_default_settings()

        if self.widgetResults:
            self.widgetResults.sig_widget_results_destroying.emit()
            self.widgetResults.deleteLater()

    @Slot()
    def cleanWindow(self):
        for i in reversed(range(self.layout.count())):
            widgetToRemove = self.layout.itemAt(i).widget()
            widgetToRemove.deleteLater()

    @Slot()
    def quit_app(self):
        self.app.quit()

    def closeEvent(self, event):
        self.quit_app()
