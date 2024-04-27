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
    """Un chart (un diagramme à barres empilées) pour des règles de vote à plusieurs tours"""

    def __init__(self, voting_rule: str, parent: QGraphicsItem = None):
        """Initialise un diagramme à barres empilées. Initialise une instance d'élection (pour le partage des données).
        Initialise les axes, les bars. Remplit le diagramme avec les résultats d'une règle de vote `voting_rule`.

        Args:
            voting_rule (str): Une constante d'une règle du vote.
            parent (PySide6.QtWidgets.QGraphicsItem): Un parent d'un diagramme. Default = `None`.
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
        """Initialise les bars pour chaque candidat avec leurs scores. Ajoute une bordure
        pour le bar du candidat-gagnant. Construit un dictionnaire qui associe un candidat avec son barset."""

        # Dict: key = candidat, value = sont barset
        barset_dict = dict()
        winner = self.election.choose_winner(self.voting_rule)

        for cand in self.election.candidates:
            barSet = QBarSet(f"{cand.first_name} {cand.last_name}", parent=self)
            barset_dict[cand] = barSet

        # Ajouter des scores aux barset
        for i in range(len(self.election.results[self.voting_rule])):
            result_round = self.election.results[self.voting_rule][i]
            for cand in result_round:
                candBarSet = barset_dict[cand]
                candBarSet.append(cand.scores[self.voting_rule][i])

        # Ajouter des barset à series avec le barset du gagnant en haut
        for candidate, barset in barset_dict.items():
            if candidate != winner:
                self.series.append(barset)
        self.series.append(barset_dict[winner])

        barset_dict[winner].setBorderColor(QColor("black"))

    def initAxis(self) -> None:
        """Initialise les axes. L'axe verticale corredpond aux scores. L'axe horizontal correspond aux tours."""

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
        """Calcule le maximum de l'axe vertical. Le maximum est le nombre d'électeurs qui participent à l'élection.

        Returns:
            int: Un maximum pour l'axe vertical.
        """

        return len(self.election.electors)
