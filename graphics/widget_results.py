from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from .widget_results_utls import DirectedGraph
from .widget_results_utls import GraphsView

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

        # Verifier si l'un des condorcet a ete choisi
        # Si oui, init directed graph
        if self.condorcetChosen():
            self.initDirectedGraph()

    # Returns True if one the condorcet method was chosen
    def condorcetChosen(self):
        setCondorcet = {CONDORCET_SIMPLE, CONDORCET_COPELAND, CONDORCET_SIMPSON}
        return bool(setCondorcet & self.election.results.keys())

    def initUI(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(10)

    # Affichage des resultats sous la forme d'un tableau
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
            show_graph_btn = QPushButton(parent=self)

            label_voting_rule.setObjectName(voting_rule)
            label_winner.setObjectName(f"{voting_rule}_winner")
            show_graph_btn.setObjectName(f"{voting_rule}_btn")

            if voting_rule == CONDORCET_SIMPLE or voting_rule == CONDORCET_COPELAND:
                show_graph_btn.clicked.connect(self.showDirectedGraph)
            if voting_rule == CONDORCET_SIMPSON:
                show_graph_btn.clicked.connect(lambda: self.showDirectedGraph(True))

            label_voting_rule.setText(names[voting_rule])

            winner = self.election.choose_winner(voting_rule)

            # None can be in condorcet simple
            if winner is not None:
                label_winner.setText(f"{winner.first_name} {winner.last_name}")
            else:
                label_winner.setText("No winner")

            show_graph_btn.setText("Show graph")
            self.layout.addWidget(label_voting_rule, row, 0, alignment=Qt.AlignHCenter)
            self.layout.addWidget(label_winner, row, 1, alignment=Qt.AlignHCenter)
            self.layout.addWidget(show_graph_btn, row, 2, alignment=Qt.AlignHCenter)

    def initDirectedGraph(self):
        self.scene = DirectedGraph(parent=self)
        self.view = GraphsView(self.scene)

    # Button handler : condorcet simple, copeland
    def showDirectedGraph(self, weighted=False):
        self.scene.drawGraphics(weighted)
        self.view.show()
