from functools import partial

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Slot, Signal

from .widget_results_utls import (
    DirectedGraph,
    DirectedGraphView,
    ChartView,
)

from .ui_constants import UI_VOTING_RULES

from electoral_systems import Election
from electoral_systems.voting_rules.constants import *


class WidgetResults(QWidget):
    sig_show_chart = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.election = Election()
        self.initUI()
        self.initLabels()
        self.initViews()

    def initViews(self):
        if self.condorcetChosen():
            self.initDirectedGraph()

        self.oneRoundBool, oneRoundSet = self.oneRoundChosen()
        self.multiRoundBool, multiRoundSet = self.multiRoundChosen()

        if self.oneRoundBool or self.multiRoundBool:
            self.initChartsView()

        if self.oneRoundBool:
            self.charts_view.initOneRoundChart(oneRoundSet)

        if self.multiRoundBool:
            self.charts_view.initMultiRoundChart(multiRoundSet)

    # Returns True iff veto, plurality(1 round), veto, borda or approval was chosen
    def oneRoundChosen(self):
        setOneRound = {PLURALITY_SIMPLE, VETO, BORDA, APPROVAL}
        intersect = setOneRound & self.election.results.keys()
        return bool(intersect), intersect

    # Returns True iff one the condorcet method was chosen
    def condorcetChosen(self):
        setCondorcet = {CONDORCET_SIMPLE, CONDORCET_COPELAND, CONDORCET_SIMPSON}
        return bool(setCondorcet & self.election.results.keys())

    def multiRoundChosen(self):
        setMultiRound = {PLURALITY_2_ROUNDS, EXHAUSTIVE_BALLOT}
        intersect = setMultiRound & self.election.results.keys()
        return bool(intersect), intersect

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
            show_btn = QPushButton(parent=self)

            # Connect buttons to emitting signals
            if voting_rule in {CONDORCET_SIMPLE, CONDORCET_COPELAND}:
                show_btn.clicked.connect(self.showDirectedGraph)
                show_btn.setText("Show graph")
            elif voting_rule == CONDORCET_SIMPSON:
                show_btn.clicked.connect(lambda: self.showDirectedGraph(True))
                show_btn.setText("Show graph")
            else:
                show_btn.clicked.connect(partial(self.onShowChartBtnClick, voting_rule))
                show_btn.setText("Show chart")

            label_voting_rule.setText(UI_VOTING_RULES[voting_rule])
            winner = self.election.choose_winner(voting_rule)

            # None can be in condorcet simple
            if winner is None:
                label_winner.setText("No winner")
            else:
                label_winner.setText(f"{winner.first_name} {winner.last_name}")

            self.layout.addWidget(label_voting_rule, row, 0, alignment=Qt.AlignHCenter)
            self.layout.addWidget(label_winner, row, 1, alignment=Qt.AlignHCenter)
            self.layout.addWidget(show_btn, row, 2, alignment=Qt.AlignHCenter)

    def initDirectedGraph(self):
        self.graph_scene = DirectedGraph(parent=self)
        self.graph_view = DirectedGraphView(self.graph_scene)

    @Slot(bool)
    def showDirectedGraph(self, weighted=False):
        self.graph_scene.drawGraphics(weighted)
        self.graph_view.show()

    def initChartsView(self):
        self.charts_view = ChartView()
        self.sig_show_chart.connect(self.charts_view.setChartBySig)

    @Slot(str)
    def onShowChartBtnClick(self, voting_rule):
        self.sig_show_chart.emit(voting_rule)
