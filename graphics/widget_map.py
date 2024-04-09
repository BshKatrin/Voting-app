"""Un module définissant une classe `WidgetMap`.

Ce module fournit une classe `WidgetMap` qui représente un widget pour une carte politique,
la génération des données et le choix des règles de vote

Attributs:
    Widgets:
        - voting_rules_checkbox (graphics.widget_map_utls.widget_checkbox.WidgetCheckbox): un widget avec des checkboxes
            correspondant aus règles du vote.
        - choose_voting_rules_btn (PySide6.QtWidgets.QPushButton): un button pour afficher un widget avec des checkboxes.
        - start_election_btn (PySide6.QtWidgets.QPushButton): un button pour commencer une élection.
        - quadrant_map (graphics.widget_map_utls.quadrant_map.QuadrantMap): un widget qui déssine une carte politique.
        - widget_settings (graphics.widget_map_utls.widget_random_settings.WidgetRandomSettings) : un widget avec des réglages 
            des paramètres pour une génération des données.
        - candidates_text_box: un champ de saisie du nombre des candidats à générer aléatoirement.
        - electors_text_box: un champ de saisie du nombre des électeurs à générer aléatoirement.
        - btn_gen_random: un button pour confirmer les nombres entrés dans les champs de saisie.
        - random_settings_btn: un button pour ouvrir un widget avec des réglages de la génération des données.

    Données d'une élection:
        - election (electoral_systems.election.Election) : une instance de la classe `Election` pour partager les données entre les widgets.

Methodes:
    - initUI: Une méthode qui initialise une interface complet d'un widget.
    - initNavigation: Une méthode qui initialise une partie d'interface avec des buttons.
        qui permettent d'afficher un widget avec des checkboxes et lancer une élection.
    - initInputFields: Une méthode qui initialise une partie d'interface consacré à la génération des données.
    - getIntInputField: Une méthode permettant de recevoir un entier du champ de saisie.

Slots:
    - generateData: Un slot qui génére des candidats et des électeurs aléatoirement.
    - onStartElectionClick: Un slot qui émet le signal `sig_start_election` lorsque le button de lancer une élection a été cliqué.
    - toggleElectionBtnState: Un slot qui active ou désactive le button pour lancer une élection.
    - showWidgetCheckbox: Un slot qui permet d'afficher un widgets avec des checkboxes.
    - showWidgetRandomSettings: Un slot qui permet d'afficher un widget avec des réglages de la génération des données.
    - cleanTextBoxes: Un slot qui nettoie les contenus des champs de saisie.
    - destroyChildren: Un slot qui détruit des 'widgets-enfants' dont parent a été remis à `None`.


Signals:
    - sig_start_election (PySide6.QtCore.QSignal): Un signal émis avec une liste des règles du vote choisis à l'aide des checkboxes.
"""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QSizePolicy,
)

from .widget_map_utls import QuadrantMap, WidgetCheckbox, WidgetRandomSettings

from electoral_systems import Election


class WidgetMap(QWidget):
    sig_start_election = Signal(list)

    def __init__(self, parent: QWidget):
        """Initialisation de la taille et d'une interface d'un widget.

        Args:
            parent (PySide6.QtWidgets.QWidget): Un parent d'un widget.
        """

        super().__init__(parent)

        self.election = Election()

        self.setGeometry(0, 0, parent.width(), parent.height())
        self.initUI()

    def initUI(self) -> None:
        """Initialisation d'un layout et d'une interface complète."""

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.initNavigation()

        # La carte politique
        self.quadrant_map = QuadrantMap(0.8, parent=self)
        self.layout.addWidget(self.quadrant_map, 0, Qt.AlignHCenter)

        self.initInputFields()

    def initNavigation(self) -> None:
        """Initialisation des buttons qui permettent d'ouvrir un widget avec les checkboxes pour choisir des règles du vote
        et de lancer une élection."""

        # Layout pour le buttons en haut
        layout_btns = QHBoxLayout()

        # Voting rules checkbox
        self.voting_rules_checkbox = WidgetCheckbox(parent=None)
        self.voting_rules_checkbox.sig_toggle_election_btn.connect(
            self.toggleElectionBtnState
        )

        self.choose_voting_rules_btn = QPushButton(
            "Choose voting rules", parent=self)
        self.choose_voting_rules_btn.clicked.connect(self.showWidgetCheckbox)

        self.start_election_btn = QPushButton("Start election", parent=self)
        if not self.election.nb_polls:
            self.start_election_btn.setEnabled(False)
        self.start_election_btn.clicked.connect(self.onStartElectionClick)

        layout_btns.addWidget(self.choose_voting_rules_btn)
        layout_btns.addWidget(self.start_election_btn)

        self.layout.addLayout(layout_btns)

    def initInputFields(self) -> None:
        """Initialisation des champs de saisie du nombre des candidats et des électeurs à générer aléatoirement, 
        des buttons pour confirmer les nombres saisis et pour ouvrir un widget avec des réglages des paramètres
        de la génération des données."""

        # Layout pour les widgets en bas
        layout_input = QGridLayout()

        self.widget_settings = WidgetRandomSettings(self.parent().size())

        # User input for random data
        self.candidates_text_box = QLineEdit(parent=self)
        self.candidates_text_box.setPlaceholderText("Number of candidates")

        self.electors_text_box = QLineEdit(parent=self)
        self.electors_text_box.setPlaceholderText("Number of electors")

        # Button to generate data
        self.btn_gen_random = QPushButton("Generate random", parent=self)
        self.btn_gen_random.clicked.connect(self.generateData)
        self.btn_gen_random.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Preferred,
                        QSizePolicy.Policy.Preferred)
        )

        # Button to configure data generation
        self.random_settings_btn = QPushButton(
            "Random generation settings", parent=self
        )
        self.random_settings_btn.clicked.connect(self.showWidgetRandomSettings)
        self.random_settings_btn.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Preferred,
                        QSizePolicy.Policy.Preferred)
        )

        layout_input.addWidget(self.candidates_text_box, 0, 0)
        layout_input.addWidget(self.electors_text_box, 1, 0)
        layout_input.addWidget(self.random_settings_btn, 0, 1)
        layout_input.addWidget(self.btn_gen_random, 1, 1)

        # Bottom buttons (input fields)
        self.layout.addLayout(layout_input)

    def getIntInputField(self, text_box: QLineEdit) -> int:
        """Convertir une chaîne de caractères saisie en un entier.

        Args:
            text_box (PySide6.QtWidgets.QLineEdit): un champ de saisie dont le text il faut convertir en un entier.

        Returns:
            int: un entier saisie ou 0 si la chaîne de caractères contient des caractères autres que des entiers.
        """
        text = text_box.text()
        return int(text) if text.isdigit() else 0

    @Slot()
    def generateData(self) -> None:
        """Générer les candidats et les électeurs selon les entiers entrée dans dans les champs de saisie.
        Redessiner une carte politique avec supprimer le text dans les champs de saisie."""
        nb_candidates = self.getIntInputField(self.candidates_text_box)
        nb_electors = self.getIntInputField(self.electors_text_box)

        for _ in range(nb_candidates):
            # Normalized
            generated_position = self.quadrant_map.generatePosition()
            self.election.add_candidate(generated_position)

        for _ in range(nb_electors):
            # Normalized
            generated_position = self.quadrant_map.generatePosition()
            self.election.add_elector(generated_position)

        self.quadrant_map.update()
        self.cleanTextBoxes()

    @Slot()
    def onStartElectionClick(self) -> None:
        """Appelé lorsque le button `start_election_btn` est cliqué.
        Émettre un signal `sig_start_election` avec une liste des constantes correpondant
        règles du vote choisie dans un widget avec des checkboxes."""
        chosen_voting_rule = self.voting_rules_checkbox.getChosenVotingRules()
        self.sig_start_election.emit(list(chosen_voting_rule))

    @Slot()
    def toggleElectionBtnState(self, enable: bool) -> None:
        """Activer ou désactiver le button `start_election_btn`.

        Args:
            enable (bool): Si True, alors activer le button. Sinon, le désactiver.
        """

        self.start_election_btn.setEnabled(enable)

    @Slot()
    def showWidgetCheckbox(self) -> None:
        """Afficher un widget avec des checkboxes"""

        self.voting_rules_checkbox.showCustom()

    @Slot()
    def showWidgetRandomSettings(self) -> None:
        """Afficher un widget avec des réglages des paramètres de la génération des données"""

        self.widget_settings.show()

    @Slot()
    def cleanTextBoxes(self) -> None:
        """Supprimer le contenu des champs de saisie du nombre des candidats et des électeurs à générer."""

        self.candidates_text_box.clear()
        self.electors_text_box.clear()

    @Slot()
    def destroyChildren(self) -> None:
        """Supprimer les widget-enfants d'un widget dont le parent à été remis à `None`."""
        self.voting_rules_checkbox.deleteLater()
        self.widget_settings.deleteLater()
