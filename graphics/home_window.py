from electoral_systems import Election
from os import remove
import sqlite3
from typing import List


from PySide6.QtCore import Qt, Slot, Signal, QTimer
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QApplication
)

from .home_window_utls import SettingsWidget
from .widget_map import WidgetMap
from .widget_results import WidgetResults

from sqlite import ImportData, ExportData


class HomeWindow(QMainWindow):
    """A widget which represents the main window of the app."""

    sig_data_imported = Signal(bool)
    """A signal which indicates if data of the election was imported with/without results."""

    def __init__(self, app: QApplication):
        """Initialize an instance of the election (for data sharing).

        Args:
            app (PySide6.QtWidgets.QApplication): The app.
        """

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

        self.widget_results = None
        self.widget_map = None

        self.sig_data_imported.connect(self.switchWidgetImport)

        self.createActions()
        self.createMenus()

        self.initUIHome()

    def setScreenGeometry(self) -> None:
        """Set the size of main window, put it in the middle of the screnn."""

        # Find the center 
        x = self.app.primaryScreen().availableGeometry().x()
        screen_size = self.app.primaryScreen().availableSize()
        center_x = screen_size.width() / 2 + x

        side_size = min(screen_size.height(), screen_size.width()) * 0.9
        self.setGeometry(center_x - side_size / 2, 0, side_size, side_size)

    def createActions(self) -> None:
        """Initialize the menu functionnality."""

        # Import
        self.import_with_results = QAction("Import with results", self)
        self.import_no_results = QAction("Import without results", self)

        self.import_with_results.triggered.connect(
            lambda: self.importData(True))
        self.import_no_results.triggered.connect(
            lambda: self.importData(False))

        # Export
        self.export_with_results = QAction("Export with results", self)
        self.export_no_results = QAction("Export without results", self)

        self.export_with_results.triggered.connect(
            lambda: self.exportData(True))
        self.export_no_results.triggered.connect(
            lambda: self.exportData(False))

    def createMenus(self) -> None:
        """Initialize the menu, place sub-menus et possible options."""

        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        file_menu = menu_bar.addMenu("File")

        import_menu = file_menu.addMenu("Import")
        import_menu.addAction(self.import_with_results)
        import_menu.addAction(self.import_no_results)

        export_menu = file_menu.addMenu("Export")
        export_menu.addAction(self.export_with_results)
        export_menu.addAction(self.export_no_results)

    @ Slot(str)
    def showPopupMsg(self, msg: str) -> None:
        """Initialize the pop-up with an alert and a corresponding message.
        The pop-up will be closed automatically after 2 seconds.

        Args:
            msg (str): A message to place on the pop-up.
        """

        popup = QMessageBox(parent=self.main_widget)
        popup.setIcon(QMessageBox.Icon.Warning)
        popup.setText(msg)
        popup.addButton(QMessageBox.StandardButton.Close)
        # close pop-up automatically after 2 seconds
        timer_close = QTimer()
        timer_close.singleShot(2000, popup, popup.close)
        popup.exec()

    @ Slot(bool)
    def importData(self, with_results: bool) -> None:
        """Import data with or without results. If an error occured, a pop-up will appear it indicating. 

        Args:
            with_results (bool): If `False`, import only the data of candidates and electors.
                If `True`, results of the election will be imported as well.
        """

        db_file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose database", "", "SQLite databases : (*.db)"
        )

        # Do nothing if no file was chosen
        if not db_file_path:
            return

        connection = sqlite3.connect(db_file_path)
        success, msg = ImportData.import_people(connection, with_results)
        connection.close()
        if not success:
            self.showPopupMsg(msg)
        else:
            self.sig_data_imported.emit(with_results)

    @ Slot(bool)
    def exportData(self, with_results: bool) -> None:
        """Export data with or without results. If an error occured, a pop-up will appear it indicating. 

        Args:
            with_results (bool): If `False`, export only the data of candidates and electors.
                If `True`, results of the election will be imported as well.
        """

        db_file_path, _ = QFileDialog.getSaveFileName(
            self, "Save database", "", "SQLite databases : (*.db)"
        )

        # Do nothing if no file was chosen
        if not db_file_path:
            return

        connection = sqlite3.connect(db_file_path)
        success, msg = ExportData.create_database_people(connection)

        if not success:
            self.showPopupMsg(msg)
            remove(db_file_path)

        if success and with_results:
            success, msg = ExportData.create_database_results(connection)

            if not success:
                self.showPopupMsg(msg)
                remove(db_file_path)

        connection.close()

    def toggleIEOptions(self, type: str, with_results_status: bool, no_results_status: bool) -> None:
        """Toggle the options (import, export) in the menu.

        Args:
            type (str): A constant indicating type of option: Import or Export.
                Cf. `sqlite.export_data.ExportData.EXPORT` and  `sqlite.import_data.ImportData.IMPORT`
            with_results_status (bool): An indication if an option to import/export with results should activated/desactivated.
                If `True`, activate it. If `False`, desactivate it.
            no_results_status (bool): An indication if an option to import/export without results should activated/desactivated.
                If `True`, activate it. If `False`, desactivate it.
        """

        if type == ImportData.IMPORT:
            self.import_with_results.setEnabled(with_results_status)
            self.import_no_results.setEnabled(no_results_status)
        if type == ExportData.EXPORT:
            self.export_with_results.setEnabled(with_results_status)
            self.export_no_results.setEnabled(no_results_status)

    @ Slot(bool)
    def switchWidgetImport(self, with_results: bool) -> None:
        """Change the widget on the main window if data has been imported. If the results were imported,
            show the page with results. If not, show the page with the political map.

        Args:
            with_results (bool): An indication if results has been imported. If `True`, then the results has been imported. 
                If not, `False`.
        """

        self.cleanWindow()
        if not with_results:
            self.initUIMap()
            return

        self.election.start_election(imported=True)
        self.initUIResults()

    def initNavigation(self) -> None:
        """Initialize the navigation to return to the main page from other widgets."""

        self.button_home = QPushButton("Home", parent=self)
        self.button_home.clicked.connect(self.backHomeWindow)
        self.layout.addWidget(self.button_home)

    def initUIHome(self) -> None:
        """Initialize the main page."""

        widget_btns = QWidget(parent=self.main_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
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
        quit_btn.clicked.connect(self.quitApp)

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

    @ Slot()
    def initUISettings(self) -> None:
        """Initialize the widget with the election settings."""

        self.cleanWindow()
        settings_widget = SettingsWidget(self)
        self.layout.addWidget(
            settings_widget,
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
        )
        settings_widget.sig_saved.connect(self.saveSettings)

    @ Slot()
    def saveSettings(self) -> None:
        """Delete the widget with setting et return to the main page."""

        self.cleanWindow()
        self.initUIHome()

    @ Slot()
    def initUIMap(self) -> None:
        """Clean the main window, initialize the navigation and the widget with the political map."""

        self.cleanWindow()

        self.initNavigation()

        self.toggleIEOptions(ExportData.EXPORT, False, True)
        self.toggleIEOptions(ImportData.IMPORT, False, True)

        self.widget_map = WidgetMap(parent=self.main_widget)
        self.widget_map.sig_start_election.connect(self.startElection)
        self.layout.addWidget(self.widget_map)

    @ Slot()
    def initUIResults(self) -> None:
        """Clean the main window, initialize the navigation and the widget with the election results"""

        self.cleanWindow()

        self.initNavigation()
        self.toggleIEOptions(ExportData.EXPORT, True, True)
        self.toggleIEOptions(ImportData.IMPORT, False, False)

        self.widget_results = WidgetResults(parent=self.main_widget)
        self.layout.addWidget(self.widget_results, alignment=Qt.AlignTop)

    @ Slot(list)
    def startElection(self, chosen_voting_rules: List[str]) -> None:
        """Delete the widget with the potilical map, calculate the election results, 
        initialize the widget with results.

        Args:
            chosen_voting_rules (List[str]): A list of constants related to the voting rules used in the election.
        """

        self.election.start_election(chosen_voting_rules=chosen_voting_rules)
        self.initUIResults()

    @ Slot()
    def backHomeWindow(self) -> None:
        """Clean the main window, initialize the main page, delete all data of the election.
        The settings of the election are not changed."""

        self.cleanWindow()
        self.initUIHome()

        self.election.delete_all_data()

    @ Slot()
    def cleanWindow(self) -> None:
        """Delete all widgets placed on the main window."""

        for i in reversed(range(self.layout.count())):
            widget_to_remove = self.layout.itemAt(i).widget()

            if widget_to_remove == self.widget_map:
                self.widget_map.destroyChildren()

            if widget_to_remove == self.widget_results:
                self.widget_results.destroyChildren()

            widget_to_remove.deleteLater()

    @ Slot()
    def quitApp(self) -> None:
        """Close the app."""
        
        self.app.quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Redefinition of the`closeEvent`. Close the app on the main window closure."""

        self.quitApp()
        event.accept()
