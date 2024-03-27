from functools import partial

from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QPushButton,
    QCheckBox,
)
from PySide6.QtCore import Qt, Slot, Signal, QSize

from .widget_results_utls import DirectedGraph, DirectedGraphView, ChartView, MapImage

from .ui_constants import UI_VOTING_RULES

from electoral_systems import Election
from electoral_systems.voting_rules.constants import *


class WidgetResults(QWidget):
    sig_show_chart = Signal(str)
    sig_widget_results_destroying = Signal()
    sig_conduct_poll = Signal(int)

    def __init__(self, parent):
        super().__init__(parent)

        self.election = Election()

        self.setGeometry(0, 0, parent.width(), parent.height())
        # For destroy_children
        self.graph_view = None
        self.charts_view = None
        # True if nb_polls != 0, False otherwise
        self.conduct_polls = True if self.election.nb_polls else False
        self.initUI()
        self.initViews()

        self.sig_widget_results_destroying.connect(self.destroyChildren)

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
        # Add polls row only if nb_polls != 0
        if self.conduct_polls:
            self.initPollsUI()

        self.initColumns()

        self.image = MapImage("graphics/temp/map.png")
        self.image.closed.connect(self.toggleCheckbox)

    def initPollsUI(self):
        # Number of polls
        self.nb_polls_conducted = 1

        remaining_polls_label = QLabel(self)
        remaining_polls_label.setStyleSheet("font-weight: bold")
        remaining_polls_label.setText(
            f"Polls {self.nb_polls_conducted}/{self.election.nb_polls}"
        )

        start_poll_btn = QPushButton("Apply new poll", self)
        start_poll_btn.clicked.connect(
            partial(self.conductNewPoll, self.nb_polls_conducted + 1)
        )

        # Add to layout (on the very top)
        self.layout.addWidget(
            remaining_polls_label, 0, 0, Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addWidget(start_poll_btn, 0, 1, 1, 3)

    # Affichage des resultats sous la forme d'un tableau
    def initColumns(self):
        start_row = 1 if self.conduct_polls else 0

        column_one_header = QLabel()
        column_one_header.setText("Voting rule")
        self.layout.addWidget(
            column_one_header, start_row, 0, alignment=Qt.AlignHCenter
        )
        column_one_header.setStyleSheet("font-weight: bold")

        column_two_header = QLabel()
        column_two_header.setText("Winner")
        self.layout.addWidget(
            column_two_header, start_row, 1, alignment=Qt.AlignHCenter
        )
        column_two_header.setStyleSheet("font-weight: bold")

        column_three_header = QLabel()
        column_three_header.setText("Satisfaction")
        self.layout.addWidget(
            column_three_header, start_row, 2, alignment=Qt.AlignHCenter
        )
        column_three_header.setStyleSheet("font-weight: bold")

        self.checkbox = QCheckBox("Show quadrant map", parent=self)
        self.checkbox.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.checkbox.stateChanged.connect(self.toggleQuadrantMap)
        self.layout.addWidget(
            self.checkbox, start_row, 3, Qt.AlignRight | Qt.AlignVCenter
        )

        self.election.calculate_results()

        for row, voting_rule in enumerate(self.election.results, start=start_row + 1):
            # Create label with name to find it later with findChild if necessary
            label_voting_rule = QLabel(parent=self)
            label_winner = QLabel(parent=self)
            label_satisfaction = QLabel(parent=self)

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

            satisfaction = self.election.calculate_satisfaction(winner)
            label_satisfaction.setText(f"{satisfaction:.2f}")

            self.layout.addWidget(label_voting_rule, row, 0, alignment=Qt.AlignHCenter)
            self.layout.addWidget(label_winner, row, 1, alignment=Qt.AlignHCenter)
            self.layout.addWidget(label_satisfaction, row, 2, alignment=Qt.AlignHCenter)

            self.layout.addWidget(show_btn, row, 3, alignment=Qt.AlignHCenter)

    @Slot(int)
    def conductNewPoll(self, polls_conducted):
        # Apply new poll

        # Update nb of polls
        self.nb_polls_conducted = polls_conducted
        # Desactivate button if limit is reached
        if polls_conducted == self.election.nb_polls:
            self.start_poll_btn.setEnabled(False)

    def _get_view_size(self):
        return QSize(self.parent().width() * 0.8, self.parent().height() * 0.8)

    def _resize_view(self, view):
        view.resize(self._get_view_size())

    def initDirectedGraph(self):
        self.graph_scene = DirectedGraph(self._get_view_size(), parent=self)
        self.graph_view = DirectedGraphView(self.graph_scene)
        self._resize_view(self.graph_view)

    @Slot(bool)
    def showDirectedGraph(self, weighted=False):
        self.graph_scene.drawGraphics(weighted)
        self.graph_view.show()

    def initChartsView(self):
        self.charts_view = ChartView()
        self._resize_view(self.charts_view)

        self.sig_show_chart.connect(self.charts_view.setChartBySig)

    @Slot(str)
    def onShowChartBtnClick(self, voting_rule):
        self.sig_show_chart.emit(voting_rule)

    @Slot(bool)
    def toggleQuadrantMap(self, state):
        if state and (not self.image.isVisible()):
            self.image.show()
        elif (not state) and self.image.isVisible():
            self.image.close()

    @Slot()
    def toggleCheckbox(self):
        self.checkbox.setChecked(False)

    # Destroy "child widget" whose parent is NOT set
    @Slot()
    def destroyChildren(self):
        self.image.deleteLater()
        # All Condorcet
        if self.graph_view:
            self.graph_view.deleteLater()
        # All 1 round, multi_round
        if self.charts_view:
            self.charts_view.deleteLater()
