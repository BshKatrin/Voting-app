from PySide6.QtCharts import (
    QBarSeries,
    QBarSet,
    QChart,
    QBarCategoryAxis,
    QValueAxis,
)
from PySide6.QtWidgets import QGraphicsItem

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from electoral_systems import Election, VotingRulesConstants


class ChartOneRound(QChart):
    """A chart (simple bar chart) for one round voting rules."""

    def __init__(self, voting_rule: str, parent: QGraphicsItem = None):
        """Initialize the chart. Initialize an instance of the election (for data sharing).
            Initialize axes and bars. Fill the chart with data (i.e. results of the given voting rule).

        Args:
            voting_rule (str): A constant related to the voting rule. 
            parent (PySide6.QtWidgets.QGraphicsItem): Chart's parent. Default = `None`.
        """

        super().__init__(parent)
        self.setTitle(f"{VotingRulesConstants.UI[voting_rule]} results")
        self.voting_rule = voting_rule
        self.election = Election()

        self.series = QBarSeries()
        self.addSeries(self.series)
        self.initBarSets()
        self.initAxes()

    def initBarSets(self) -> None:
        """Initialize the bars for each candidate with his scores. Highlight (i.e. add black border) the bar of the winner.
            Initialize and fill the dictionary which associates a candidate with his bar."""

        self.winner_barset = None
        # Barset for each candidate
        self.candidates_barsets = dict()

        for cand in self.election.candidates:
            barSet = QBarSet(f"{cand.first_name} {cand.last_name}")
            self.candidates_barsets[cand] = barSet

            score = cand.scores[self.voting_rule]
            barSet.append(score)

            if cand == self.election.choose_winner(self.voting_rule):
                self.winner_barset = barSet
                continue
            self.series.append(barSet)

        # Highlight winner, add it last so it can be on top
        if self.winner_barset:
            self.series.append(self.winner_barset)
            self.winner_barset.setBorderColor(QColor("black"))

    def initAxes(self) -> None:
        """Initialize the axes: vertical axe shows scores, values on the horizontal axe are hidden."""

        # X axis
        self.axisX = QBarCategoryAxis(self)
        self.axisX.append("1")
        self.axisX.setLabelsVisible(False)

        self.addAxis(self.axisX, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(self.axisX)

        # Y axis
        self.axisY = QValueAxis(self)
        self._setYRange()
        # self.axisY.applyNiceNumbers()
        self.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axisY)

    def _setYRange(self) -> None:
        """Fix the minimum and maximum values on the vertical axe."""
        mx = self._findMax()
        self.axisY.setRange(0, mx)

    def _findMax(self) -> int:
        """Find a maximum score value.

        Returns:
            int: A maximum score.
        """

        mx = -1
        for candidate in self.election.results[self.voting_rule]:
            mx = max(candidate.scores[self.voting_rule], mx)
        return mx

    def updateData(self) -> None:
        """Update candidates' scores. Update vertical axe range. Hightlight another bar if necessary (i.e. if the winner has changed). 
            Useful for polls."""

        self._setYRange()
        self.removeBarsets()
        self.reHighlight()
        for cand in self.election.candidates:
            barset = self.candidates_barsets[cand]
            barset.replace(0, cand.scores[self.voting_rule])

    def removeBarsets(self):
        """Delete bars of candidates who no longer participate in the election. Useful for polls."""

        for cand, barset in self.candidates_barsets.items():
            if cand not in self.election.candidates and barset:
                self.series.remove(barset)
                self.candidates_barsets[cand] = None

    def reHighlight(self):
        """Highlight another bar. Delete previous highlight."""
        
        winner = self.election.choose_winner(self.voting_rule)
        if self.winner_barset != self.candidates_barsets[winner]:
            self.winner_barset.setBorderColor(QColor("transparent"))
            self.candidates_barsets[winner].setBorderColor(QColor("black"))
            self.winner_barset = self.candidates_barsets[winner]
