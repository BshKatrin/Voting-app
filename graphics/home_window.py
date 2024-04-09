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
    """Un widget qui représente une fenêtre principale d'une application."""
    sig_data_imported = Signal(bool)
    """Un signal qui indique les données d'une élections ont été importées avec ou sans des résultats"""

    def __init__(self, app: QApplication):
        """Initialisation du titre, de la taille, du widget central, du layout, du menu. Initialisation de la page d'accueil

        Args:
            app (PySide6.QtWidgets.QApplication): une application
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
        """Fixer la taille de la fenêtre principale et la placer au millieu d'écran."""
        # Trouver le centre
        x = self.app.primaryScreen().availableGeometry().x()
        screen_size = self.app.primaryScreen().availableSize()
        center_x = screen_size.width() / 2 + x

        side_size = min(screen_size.height(), screen_size.width()) * 0.9
        self.setGeometry(center_x - side_size / 2, 0, side_size, side_size)

    def createActions(self) -> None:
        """Définir la fonctionnalité du menu"""
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
        """Définir le menu, placer les sous-menus et les options possibles"""
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
        """Définir un popup avec une alerte et le message correspondant.
        Un popup ferme automatiquement au bout de 2 seconds.

        Args:
            msg (str): un message à afficher
        """
        popup = QMessageBox(parent=self.main_widget)
        popup.setIcon(QMessageBox.Icon.Warning)
        popup.setText(msg)
        popup.addButton(QMessageBox.StandardButton.Close)
        # Fermer un popup automatiquement après 2 sec
        timer_close = QTimer()
        timer_close.singleShot(2000, popup, popup.close)
        popup.exec()

    @ Slot(bool)
    def importData(self, with_results: bool) -> None:
        """Importer les données avec ou sans les résultats. 
        Si l'erreur est arrivée, faire apparaître un popup avec le message

        Args:
            with_results (bool): Si False, importer uniquement les données des électeurs et des candidats.
            Sinon, importer de plus les résultats d'une élection.
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
        """Exporter les données avec ou sans les résultats. 
        Si l'erreur est arrivée, faire apparaître un popup avec le message

        Args:
            with_results (bool): Si False, exporter uniquement les données des électeurs et des candidats.
            Sinon, exporter de plus les résultats d'une élection.
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
        """Activer ou désactiver les options dans le menu par rapport à l'import et l'export.

        Args:
            type (str): Une indication de l'export ou de l'import.
            with_results_status (bool): Une indication s'il faut activer ou désactiver une option d'import/export avec les résultats.
            no_results_status (bool): Une indication s'il faut activer ou désactiver une option d'import/export sans les résultats.
        """
        if type == ImportData.IMPORT:
            self.import_with_results.setEnabled(with_results_status)
            self.import_no_results.setEnabled(no_results_status)
        if type == ExportData.EXPORT:
            self.export_with_results.setEnabled(with_results_status)
            self.export_no_results.setEnabled(no_results_status)

    @ Slot(bool)
    def switchWidgetImport(self, with_results: bool) -> None:
        """Changer le widget affiché si les données ont été importées. Si les résultats ont été importés, afficher 
        initialiser la page avec des résultats. Sinon, afficher la page avec la carte politique.

        Args:
            with_results (bool): Une indication si les résultats ont été importées.
        """
        self.cleanWindow()
        if not with_results:
            self.initUIMap()
            return

        self.election.start_election(imported=True)
        self.initUIResults()

    def initNavigation(self) -> None:
        """Initialiser la navigation pour revenir sur la page d'accueil à partir des autres widgets."""
        self.button_home = QPushButton("Home", parent=self)
        self.button_home.clicked.connect(self.backHomeWindow)
        self.layout.addWidget(self.button_home)

    def initUIHome(self) -> None:
        """Initialiser la page d'accueil."""
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
        """Initialiser le widget avec les réglages pour une élection."""
        self.cleanWindow()
        settings_widget = SettingsWidget(self)
        self.layout.addWidget(
            settings_widget,
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter,
        )
        settings_widget.sig_saved.connect(self.saveSettings)

    @ Slot()
    def saveSettings(self) -> None:
        """Supprimer le widget des réglages et revenir sur la page d'accueil."""
        self.cleanWindow()
        self.initUIHome()

    @ Slot()
    def initUIMap(self) -> None:
        """Nettoyer la fenêtre principale, initialiser la navigation et le widget correspondant à la carte politique."""
        self.cleanWindow()

        self.initNavigation()

        self.toggleIEOptions(ExportData.EXPORT, False, True)
        self.toggleIEOptions(ImportData.IMPORT, False, True)

        self.widget_map = WidgetMap(parent=self.main_widget)
        self.widget_map.sig_start_election.connect(self.startElection)
        self.layout.addWidget(self.widget_map)

    @ Slot()
    def initUIResults(self) -> None:
        """Nettoyer la fenêtre principale, initialiser la navigation et le widget avec des résultats d'une élection."""
        self.cleanWindow()

        self.initNavigation()
        self.toggleIEOptions(ExportData.EXPORT, True, True)
        self.toggleIEOptions(ImportData.IMPORT, False, False)

        self.widget_results = WidgetResults(parent=self.main_widget)
        self.layout.addWidget(self.widget_results, alignment=Qt.AlignTop)

    @ Slot(list)
    def startElection(self, chosen_voting_rules: List[str]) -> None:
        """Supprimer un widget correpospondant à la carte politique, calculer des résultats d'une élection, 
        initialiser le widget avec des résultats.

        Args:
            chosen_voting_rules (List[str]): Une listed des constantes correspondant aux règles du vote choisies pour une élection.
        """

        self.election.start_election(chosen_voting_rules=chosen_voting_rules)

        # Initialize Results page (winners, results, graphs)
        self.initUIResults()

    @ Slot()
    def backHomeWindow(self) -> None:
        """Nettoyer la fenêtre principale, initialiser la page d'accueil,
        supprimer les données d'une élection et remettre les règlages par défaut."""
        self.cleanWindow()
        self.initUIHome()

        self.election.delete_all_data()
        self.election.set_default_settings()

    @ Slot()
    def cleanWindow(self) -> None:
        """Supprimer tous les widgets placés sur la fenêtre principale."""
        for i in reversed(range(self.layout.count())):
            widget_to_remove = self.layout.itemAt(i).widget()

            if widget_to_remove == self.widget_map:
                self.widget_map.destroyChildren()

            if widget_to_remove == self.widget_results:
                self.widget_results.destroyChildren()

            widget_to_remove.deleteLater()

    @ Slot()
    def quitApp(self) -> None:
        """Fermer l'application."""
        self.app.quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Redéfinition d'un `closeEvent`. Fermer une application lorsque une fenêtre principale est fermée."""
        self.quitApp()
