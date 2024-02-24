from PySide6.QtCharts import (
    QStackedBarSeries,
    QChart,
    QBarSet,
    QBarCategoryAxis,
    QValueAxis,
)
from PySide6.QtCore import Qt

from electoral_systems import Election


class ChartMultiRound(QChart):
    def __init__(self, voting_rule):
        super().__init__()
        self.voting_rule = voting_rule
        self.election = Election()
        self.series = QStackedBarSeries(parent=self)

        self.initBarSets()
        self.initAxis()
        self.addSeries(self.series)

    def initBarSets(self):
        # Create dict: key = candidate, value = its barset
        barSetDict = dict()
        for cand in self.election.candidates:
            barSet = QBarSet(f"{cand.first_name} {cand.last_name}", parent=self)
            barSetDict[cand] = barSet

        # Add scores to barSet so that candidats are positioned from the least to the best
        for i in range(len(self.election.results[self.voting_rule])):
            result_round = self.election.results[self.voting_rule][i]
            for cand in result_round:
                candBarSet = barSetDict[cand]
                candBarSet.append(cand.scores[self.voting_rule][i])

        # Add all barSet to series
        for barSet in barSetDict.values():
            self.series.append(barSet)

    def initAxis(self):
        # Set axis X
        self.axisX = QBarCategoryAxis(parent=self)
        result_rounds = self.election.results[self.voting_rule]
        rounds = [f"{i+1} round" for i in range(len(result_rounds))]
        self.axisX.append(rounds)
        self.addAxis(self.axisX, Qt.Alignment.AlignBottom)
        self.series.attachAxis(self.axisX)

        # Set axis Y
        self.axisY = QValueAxis(parent=self)
        self.axisY.setRange(0, self.findMax() + 5)
        self.axisY.applyNiceNumbers()
        self.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axisY)

    def findMax(self):
        # Max = sum of all scores in the first round
        try:
            fst_round = self.election.results[self.voting_rule][0]
            return sum([cand.scores[self.voting_rule][0] for cand in fst_round])
        except IndexError:
            return 0
