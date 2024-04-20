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
    """Une classe qui représente un widget avec une carte politique, la génération des données et le choix des règles de vote."""

    sig_start_election = Signal(list)
    """Un signal émis avec une liste des constantes associées aux règles de vote choisies à l'aide des checkboxes."""

    def __init__(self, parent: QWidget):
        """Initialise une instance  d'élection (pour le partage des données).

        Args:
            parent (PySide6.QtWidgets.QWidget): Le parent d'un widget.
        """

        super().__init__(parent)

        self.election = Election()

        self.setGeometry(0, 0, parent.width(), parent.height())
        self.initUI()

    def initUI(self) -> None:
        """Initialise un layout et UI (les bouttons, les champs de saisie et la carte politique)."""

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.initNavigation()

        # La carte politique
        self.quadrant_map = QuadrantMap(0.8, parent=self)
        self.layout.addWidget(self.quadrant_map, 0, Qt.AlignHCenter)

        self.initInputFields()

    def initNavigation(self) -> None:
        """Initialise des bouttons qui permettent de lancer une élection et d'ouvrir un widget avec
            les checkboxes pour choisir des règles de vote."""

        # Layout pour le buttons en haut
        layout_btns = QHBoxLayout()

        # Widget-checkbox pour choisir des règles du vote
        self.voting_rules_checkbox = WidgetCheckbox(parent=None)
        self.voting_rules_checkbox.sig_toggle_election_btn.connect(
            self.toggleElectionBtnState
        )

        self.choose_voting_rules_btn = QPushButton(
            "Choose voting rules", parent=self)
        self.choose_voting_rules_btn.clicked.connect(self.showWidgetCheckbox)

        self.start_election_btn = QPushButton("Start election", parent=self)

        # Le button est activé uniquement si
        # Il existe des électeurs et des candidats et au moins une règle du vote a été choisie
        if (not self.election.has_electors_candidates()) or (not self.voting_rules_checkbox.votingRuleChosen()):
            self.start_election_btn.setEnabled(False)

        self.start_election_btn.clicked.connect(self.onStartElectionClick)

        layout_btns.addWidget(self.choose_voting_rules_btn)
        layout_btns.addWidget(self.start_election_btn)

        self.layout.addLayout(layout_btns)

    def initInputFields(self) -> None:
        """Initialise les champs de saisie du nombre des candidats et des électeurs à générer aléatoirement, 
        les bouttons pour confirmer les nombres saisis et pour ouvrir un widget avec les réglages des paramètres
        de la génération des données."""

        # Layout pour les widgets en bas
        layout_input = QGridLayout()

        self.widget_settings = WidgetRandomSettings(self.parent().size())

        # Input de l'utilisateur pour générer les données aléatoires
        self.candidates_text_box = QLineEdit(parent=self)
        self.candidates_text_box.setPlaceholderText("Number of candidates")

        self.electors_text_box = QLineEdit(parent=self)
        self.electors_text_box.setPlaceholderText("Number of electors")

        # Les buttons pour générer les données
        self.btn_gen_random = QPushButton("Generate random", parent=self)
        self.btn_gen_random.clicked.connect(self.generateData)

        if not self.election.has_electors_candidates():
            self.btn_gen_random.clicked.connect(self.toggleElectionBtnState)

        self.btn_gen_random.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Preferred,
                        QSizePolicy.Policy.Preferred)
        )

        # Button pour configurer les paramètres de la génération des données
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

        self.layout.addLayout(layout_input)

    def getIntInputField(self, text_box: QLineEdit) -> int:
        """Convertit une chaîne de caractères saisie en un entier.

        Args:
            text_box (PySide6.QtWidgets.QLineEdit): Un champ de saisie dont le text il faut convertir en un entier.

        Returns:
            int: Un entier saisie ou 0 si la chaîne de caractères contient des caractères autres que des entiers.
        """

        text = text_box.text()
        return int(text) if text.isdigit() else 0

    @Slot()
    def generateData(self) -> None:
        """Génére les candidats et les électeurs selon les entiers entrés dans dans les champs de saisie.
        Redessine la carte politique et supprime le texte dans les champs de saisie."""

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
        """Émet un signal `sig_start_election` avec une liste des constantes correpondantes aux
        règles de vote choisies dans le widget avec des checkboxes. 
        Appelée lorsque le boutton `start_election_btn` est cliqué.
        """

        chosen_voting_rule = self.voting_rules_checkbox.getChosenVotingRules()
        self.sig_start_election.emit(list(chosen_voting_rule))

    @Slot()
    def toggleElectionBtnState(self) -> None:
        """Active ou désactive le boutton `start_election_btn` qui permet de lancer une élection.
        Le boutton est activé uniquement s'il existe des électeurs et des candidats et au moins une règle de vote 
        a été choisie.
        """

        enable = self.election.has_electors_candidates() and self.voting_rules_checkbox.votingRuleChosen()
        self.start_election_btn.setEnabled(enable)

    @Slot()
    def showWidgetCheckbox(self) -> None:
        """Affiche un widget avec des checkboxes."""

        self.voting_rules_checkbox.showCustom()
        self.voting_rules_checkbox.raise_()

    @Slot()
    def showWidgetRandomSettings(self) -> None:
        """Affiche un widget avec les réglages des paramètres de la génération des données."""

        self.widget_settings.show()
        self.widget_settings.raise_()

    @Slot()
    def cleanTextBoxes(self) -> None:
        """Supprime le contenu des champs de saisie du nombre des candidats et des électeurs à générer."""

        self.candidates_text_box.clear()
        self.electors_text_box.clear()

    @Slot()
    def destroyChildren(self) -> None:
        """Supprime les widget-enfants d'un widget dont le parent à été remis à `None`."""

        self.voting_rules_checkbox.deleteLater()
        self.widget_settings.deleteLater()
