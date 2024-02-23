from PySide6.QtCharts import (
    QBarSeries,
    QBarSet,
    QChart,
    QBarCategoryAxis,
    QValueAxis,
)

from PySide6.QtCore import Qt

from electoral_systems import Election
from electoral_systems.voting_rules.constants import (
    VETO,
    PLURALITY_SIMPLE,
    BORDA,
    APPROVAL,
)

names = {
    PLURALITY_SIMPLE: "Plurality",
    VETO: "Veto",
    BORDA: "Borda",
    APPROVAL: "Approval",
}


class ChartOneRound(QChart):
    def __init__(self, voting_rules_set, parent=None):
        super().__init__(parent)
        self.setTitle("Voting rule results")
        self.voting_rules = voting_rules_set
        self.election = Election()

        self.series = QBarSeries()
        self.initBarSets()
        self.addSeries(self.series)
        self.initAxes()

    def initBarSets(self):
        # BarSet for every candidate
        for cand in self.election.candidates:
            barSet = QBarSet(f"{cand.first_name} {cand.last_name}")
            # Add scores for each chosen voting rule
            for voting_rule in self.voting_rules:
                score = cand.scores[voting_rule]
                barSet.append(score)
            self.series.append(barSet)

    def initAxes(self):
        # Set X axis
        self.axisX = QBarCategoryAxis(self)
        self.axisX.append({names[voting_rule] for voting_rule in self.voting_rules})
        self.addAxis(self.axisX, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(self.axisX)

        # Set Y axis
        self.axisY = QValueAxis(self)
        mx = self.findMax()
        self.axisY.setRange(0, mx + 5)
        self.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axisY)

    # Find maximum score (for Y axis)
    def findMax(self):
        mx = -1
        for voting_rule in self.voting_rules:
            scores = [cand.scores[voting_rule] for cand in self.election.candidates]
            mx = max(max(scores), mx)
        return mx
