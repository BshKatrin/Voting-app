from functools import partial
from typing import Set, Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, Slot
from electoral_systems import Election

from electoral_systems.voting_rules.constants import *
from electoral_systems import VotingRulesConstants
from .voting_rule_checkbox import VotingRuleCheckbox


class WidgetCheckbox(QWidget):
    """Un widget qui représente l'ensemble des checkbox pour choisir des règles de vote pour une élection."""

    sig_toggle_election_btn = Signal()
    """Un signal qui est émis lorsque le button `Confirm` est cliqué. Permet d'activer ou désactiver le button pour lancer une élection."""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialise une instance d'élection (pour le partage des données).
        Initialise la taille, le titre et UI. Si les sondages ont été activées, coche une case correspondante
        à une règle de vote pour les sondages et désactive les autres cases.

        Args:
            parent (Optional[PySide6.QtWidgets.QWidget]): Un parent d'un widget. Puisque l'idée est d'afficher le checkbox 
                dans une fenêtre séparée parent est rémis à `None` par défaut.
        """

        super().__init__(parent)
        self.election = Election()

        self.setWindowTitle("Voting rules")
        self.setGeometry(100, 100, 300, 200)

        self.chosen_voting_rules = set()
        self.initUI()

        if self.election.nb_polls:
            self.choosePollVotingRule(self.election.poll_voting_rule)
            self.disableAllVotingRules()

    def initUI(self) -> None:
        """Initialise le layout, les checkboxes pour chaque règle de vote disponible et les buttons."""

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.rule_checkbox = dict()

        for voting_rule, voting_rule_name in VotingRulesConstants.UI.items():
            # Minimum number of candidate for each voting rule
            min = 3 if voting_rule in VotingRulesConstants.MULTI_ROUND else 2

            checkbox = VotingRuleCheckbox(voting_rule_name, min, parent=self)

            checkbox.stateChanged.connect(partial(self.onStateChanged, voting_rule))
            checkbox.setEnabled(False)

            self.layout.addWidget(checkbox)
            self.rule_checkbox[voting_rule] = checkbox

        self.confirm_btn = QPushButton("Confirm", self)
        self.confirm_btn.clicked.connect(self.confirmVotingRules)

        self.choose_all_btn = QPushButton("Choose all", self)
        self.choose_all_btn.clicked.connect(self.chooseAllVotingRules)
        if self.election.nb_polls:
            self.choose_all_btn.setDisabled(True)

        self.layout.addWidget(self.confirm_btn)
        self.layout.addWidget(self.choose_all_btn)

    @Slot(str, int)
    def onStateChanged(self, voting_rule: str, state: int) -> None:
        """MAJ l'ensemble des règles de vote choisies si le checkbox correspondant a été coché ou décoché."""

        (
            self.chosen_voting_rules.add(voting_rule)
            if state
            else self.chosen_voting_rules.discard(voting_rule)
        )

    def enableCheckboxes(self) -> None:
        """Active les checkboxes à cocher dont le nombre minimum de candidats a été atteint"""
        nb_candidates = len(self.election.candidates)
        for checkbox in self.rule_checkbox.values():
            if nb_candidates >= checkbox.min:
                checkbox.setEnabled(True)

    def showCustom(self) -> None:
        """Affiche le widget."""

        if not self.election.nb_polls:
            self.enableCheckboxes()
        self.show()

    @Slot()
    def confirmVotingRules(self) -> None:
        """Émet le signal `sig_toggle_election_btn` et ferme le widget (le widget n'est pas supprimé, juste caché)."""

        self.sig_toggle_election_btn.emit()
        self.close()

    @Slot()
    def chooseAllVotingRules(self) -> None:
        """Choisit tous les checkboxes activés."""

        for checkbox in self.rule_checkbox.values():
            if checkbox.isEnabled():
                checkbox.setChecked(True)

    def getChosenVotingRules(self) -> Set[str]:
        """Retourne l'ensemble des constantes correspondantes aux règles de vote choisies avec des checkboxes.

        Returns:
            Set[str]: Un ensemble des constantes associées aux règles du vote.
        """

        return self.chosen_voting_rules

    def votingRuleChosen(self) -> bool:
        """Vérifie si au moins une règle de vote a été choisie.

        Returns:
            bool: True si au moins une règle de vote a été choisie. Sinon, False.
        """
        return bool(self.chosen_voting_rules)

    def choosePollVotingRule(self, voting_rule: str) -> None:
        """Coche le checkbox correspondant à une règle de vote `voting_rule`.

        Args:
            voting_rule (str): Une constante associée à une règle du vote dont le checkbox il faut cocher. 
        """

        self.rule_checkbox[voting_rule].setChecked(True)

    def disableAllVotingRules(self) -> None:
        """Désactive tous les checkboxes."""

        for checkbox in self.rule_checkbox.values():
            checkbox.setEnabled(False)
