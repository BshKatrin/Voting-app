from PySide6.QtWidgets import QWidget, QGridLayout, QLabel
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
    CONDORCET_SIMPLE: "Condorcet Simple",
    CONDORCET_COPELAND: "Condorcet Copeland",
    CONDORCET_SIMPSON: "Condorcet Simpson",
    EXHAUSTIVE_BALLOT: "Exhaustive Ballot",
    APPROVAL: "Approval",
}


class WidgetResults(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.election = Election()
        self.initUI()
        self.initLabels()

    def initUI(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(10)

    def initLabels(self):
        column_one_header = QLabel()
        column_one_header.setText("Voting rule")
        self.layout.addWidget(column_one_header, 0, 0, alignment=Qt.AlignHCenter)
        column_one_header.setStyleSheet("font-weight: bold")

        column_two_header = QLabel()
        column_two_header.setText("Winner")
        self.layout.addWidget(column_two_header, 0, 1, alignment=Qt.AlignHCenter)
        column_two_header.setStyleSheet("font-weight: bold")

        self.election.calculate_results()

        for row, voting_rule in enumerate(self.election.results, start=1):
            # Create label with name to find it later with findChild if necessary
            label_voting_rule = QLabel(parent=self)
            label_winner = QLabel(parent=self)

            label_voting_rule.setObjectName(voting_rule)
            label_winner.setObjectName(f"{voting_rule}_winner")

            label_voting_rule.setText(names[voting_rule])
            winner = self.election.choose_winner(voting_rule)
            label_winner.setText(f"{winner.first_name} {winner.last_name}")

            self.layout.addWidget(label_voting_rule, row, 0, alignment=Qt.AlignHCenter)
            self.layout.addWidget(label_winner, row, 1, alignment=Qt.AlignHCenter)
