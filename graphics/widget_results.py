from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

# 3ieme page : afficher des resultats des elections
# pour chaque regle de vote choisie a l'etape precendentst

# Doit afficher des resultats et ouvrir des charts assoicie
from electoral_systems import Election
from electoral_systems.voting_rules.constants import *

names = {
    PLURALITY_SIMPLE: "Plurality (1 round)",
    PLURALITY_2_ROUNDS: "Plurality (2 rounds)",
    VETO: "Veto",
    BORDA: "Borda",
    CONDORCET_SIMPLE: "Condorcet simplit",
    CONDORCET_COPELAND: "Condorcet Copeland",
    CONDORCET_SIMPSON: "Condorcet Simpson",
    EXHAUSTIVE_BALLOT: "Exhaustive ballot",
    APPROVAL: "Approval",
}


class WidgetResults(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.election = Election()
        self.initUI()
        self.initLabels()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)

    def initLabels(self):
        self.election.calculate_results()
        # Get amount of labels to create = nb of rows in a grid
        nb_labels = len(self.election.results)

        # Create labels based
        for voting_rule in self.election.results:
            # Create label with name to find it later with findChild if necessary
            label = QLabel(parent=self)
            label.setObjectName(voting_rule)
            self.layout.addWidget(label, 1, Qt.AlignTop)
            # Set text
            winner = self.election.choose_winner(voting_rule)
            label.setText(
                f"{names[voting_rule]}: {winner.first_name} {winner.last_name}"
            )
