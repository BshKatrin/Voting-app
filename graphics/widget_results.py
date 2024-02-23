from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Slot

from .widget_results_utls import (
    DirectedGraph,
    DirectedGraphView,
    ChartView,
    ChartOneRound,
)

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

        if self.condorcetChosen():
            self.initDirectedGraph()

        oneRoundBool, oneRoundSet = self.oneRoundChosen()
        if oneRoundBool:
            self.initOneRoundChart(oneRoundSet)

    # Returns True iff veto, plurality(1 round), veto, borda or approval was chosen
    def oneRoundChosen(self):
        setOneRound = {PLURALITY_SIMPLE, VETO, BORDA, APPROVAL}
        intersect = setOneRound & self.election.results.keys()
        return bool(intersect), intersect

    # Returns True iff one the condorcet method was chosen
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

            if voting_rule in {CONDORCET_SIMPLE, CONDORCET_COPELAND}:
                show_graph_btn.clicked.connect(self.showDirectedGraph)
            if voting_rule == CONDORCET_SIMPSON:
                show_graph_btn.clicked.connect(lambda: self.showDirectedGraph(True))
            if voting_rule in {PLURALITY_SIMPLE, BORDA, VETO, APPROVAL}:
                show_graph_btn.clicked.connect(self.showOneRoundChart)

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
        self.graph_scene = DirectedGraph(parent=self)
        self.graph_view = DirectedGraphView(self.graph_scene)

    @Slot()
    def showDirectedGraph(self, weighted=False):
        self.graph_scene.drawGraphics(weighted)
        self.graph_view.show()

    @Slot()
    def initOneRoundChart(self, oneRoundSet):
        self.widget_chart_one_round = ChartOneRound(oneRoundSet)
        self.view_chart_one_round = ChartView(self.widget_chart_one_round)

    # Button handler : plurality(1 round), borda, veto, approval
    def showOneRoundChart(self):
        self.view_chart_one_round.show()
