from PySide6.QtCharts import (
    QStackedBarSeries,
    QChart,
    QBarSet,
    QBarCategoryAxis,
    QValueAxis,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsItem

from electoral_systems import Election, VotingRulesConstants

class ChartMultiRound(QChart):
    """A chart (stacked bar chart) for multi-round voting rules."""

    def __init__(self, voting_rule: str, parent: QGraphicsItem = None):
        """Initialize the chart. Initialize an instance of the election (for data sharing).
            Initialize axes and bars. Fill the chart with data (i.e. results of the given voting rule).

        Args:
            voting_rule (str): A constant related to the voting rule. Une constante d'une règle du vote.
            parent (PySide6.QtWidgets.QGraphicsItem): Chart's parent. Default = `None`.
        """

        super().__init__(parent)

        self.voting_rule = voting_rule
        self.election = Election()

        self.setTitle(f"{VotingRulesConstants.UI[voting_rule]} results")
        self.series = QStackedBarSeries(parent=self)
        self.addSeries(self.series)
        self.initBarSets()
        self.initAxis()

    def initBarSets(self) -> None:
        """Initialize the bars for each candidate with his scores. Highlight (i.e. add black border) the bar of the winner.
            Initialize and fill the dictionary which associates a candidate with his bar."""

        # Dict: key = candidat, value = his barset
        barset_dict = dict()
        winner = self.election.choose_winner(self.voting_rule)

        for cand in self.election.candidates:
            barSet = QBarSet(f"{cand.first_name} {cand.last_name}", parent=self)
            barset_dict[cand] = barSet

        # Add scores to barsets 
        for i in range(len(self.election.results[self.voting_rule])):
            result_round = self.election.results[self.voting_rule][i]
            for cand in result_round:
                candBarSet = barset_dict[cand]
                candBarSet.append(cand.scores[self.voting_rule][i])

        # Add winner' barset on the top 
        for candidate, barset in barset_dict.items():
            if candidate != winner:
                self.series.append(barset)
        self.series.append(barset_dict[winner])

        barset_dict[winner].setBorderColor(QColor("black"))

    def initAxis(self) -> None:
        """Initialize the axes: vertical axe shows scores, horizontal axe shows rounds."""

        # Set axis X
        self.axisX = QBarCategoryAxis(parent=self)
        result_rounds = self.election.results[self.voting_rule]
        rounds = [f"{i+1} round" for i in range(len(result_rounds))]
        self.axisX.append(rounds)
        self.addAxis(self.axisX, Qt.Alignment.AlignBottom)
        self.series.attachAxis(self.axisX)

        # Set axis Y
        self.axisY = QValueAxis(parent=self)
        self.axisY.setRange(0, self.findMax())
        self.axisY.applyNiceNumbers()
        self.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axisY)

    def findMax(self) -> int:
        """Calculate the maximum value for the vertical axe. The maximum is the number of electors who participated in the election. 

        Returns:
            int: A maximum for the vertical axe.
        """

        return len(self.election.electors)
