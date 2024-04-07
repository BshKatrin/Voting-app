from PySide6.QtCharts import (
    QBarSeries,
    QBarSet,
    QChart,
    QBarCategoryAxis,
    QAbstractAxis,
    QValueAxis,
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from electoral_systems import Election, VotingRulesConstants


class ChartOneRound(QChart):
    def __init__(self, voting_rule, parent=None):
        super().__init__(parent)
        self.setTitle(f"{VotingRulesConstants.UI[voting_rule]} results")
        self.voting_rule = voting_rule
        self.election = Election()

        self.series = QBarSeries()
        self.addSeries(self.series)
        self.initBarSets()
        self.initAxes()

    def initBarSets(self):
        winner_barset = None
        # BarSet for every candidate
        self.candidates_barsets = dict()

        for cand in self.election.candidates:
            barSet = QBarSet(f"{cand.first_name} {cand.last_name}")
            self.candidates_barsets[cand] = barSet

            score = cand.scores[self.voting_rule]
            barSet.append(score)

            if cand == self.election.choose_winner(self.voting_rule):
                winner_barset = barSet
                continue
            self.series.append(barSet)

        # Highlight winner, add the last for it to be on top
        if winner_barset:
            self.series.append(winner_barset)
            winner_barset.setBorderColor(QColor("black"))

    def initAxes(self):
        # Set X axis
        self.axisX = QBarCategoryAxis(self)
        self.axisX.append("1")
        self.axisX.setLabelsVisible(False)

        self.addAxis(self.axisX, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(self.axisX)

        # Set Y axis
        self.axisY = QValueAxis(self)
        self._setYRange()
        # self.axisY.applyNiceNumbers()
        self.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axisY)

    def _setYRange(self):
        mx = self.findMax()
        self.axisY.setRange(0, mx)

    # Find maximum score (for Y axis)
    def findMax(self):
        mx = -1
        for candidate in self.election.results[self.voting_rule]:
            mx = max(candidate.scores[self.voting_rule], mx)
        return mx

    # For polls
    def updateData(self):
        self._setYRange()
        self.removeBarsets()
        for cand in self.election.candidates:
            barset = self.candidates_barsets[cand]
            barset.replace(0, cand.scores[self.voting_rule])

    # For polls
    def removeBarsets(self):
        for cand, barset in self.candidates_barsets.items():
            if cand not in self.election.candidates and barset:
                self.series.remove(barset)
                self.candidates_barsets[cand] = None
