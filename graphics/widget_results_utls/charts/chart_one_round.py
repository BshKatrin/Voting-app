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
    """Un chart (un diagramme à bandes) pour des règles de vote à un tour."""

    def __init__(self, voting_rule: str, parent: QGraphicsItem = None):
        """Initialise le diagramme à bandes. Initialise une instance d'élection (pour le partage des données).
        Remplit le diagramme avec les résultats d'une règle de vote `voting_rule`.

        Args:
            voting_rule (str): Une constante d'une règle de vote.
            parent (PySide6.QtWidgets.QGraphicsItem): Un parent d'un diagramme. Default = `None`.
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
        """Initialise les bars pour chaque candidat avec leurs scores. Ajoute une bordure noire (highlight)
        pour le bar du candidat-gagnant."""

        self.winner_barset = None
        # Barset pour chaque candidat
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

        # Highlight gagnant, ajouter en dernier pour qu'il soit en haut
        if self.winner_barset:
            self.series.append(self.winner_barset)
            self.winner_barset.setBorderColor(QColor("black"))

    def initAxes(self) -> None:
        """Initialise les axes. L'axe verticale correspond aux scores. Les valeurs de l'axe horizontal sont cachées."""

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
        """Fixe un intervalle des valeurs des scores."""
        mx = self._findMax()
        self.axisY.setRange(0, mx)

    def _findMax(self) -> int:
        """Trouve le score maximale.

        Returns:
            int: Un score maximale.
        """

        mx = -1
        for candidate in self.election.results[self.voting_rule]:
            mx = max(candidate.scores[self.voting_rule], mx)
        return mx

    def updateData(self) -> None:
        """MAJ les données sur les scores des candidats. MAJ de l'intervalle des scores. Change le highlight (bordure) si nécessaire 
        (si le gagnant a changé). Utile pour les sondages."""

        self._setYRange()
        self.removeBarsets()
        self.reHighlight()
        for cand in self.election.candidates:
            barset = self.candidates_barsets[cand]
            barset.replace(0, cand.scores[self.voting_rule])

    # For polls
    def removeBarsets(self):
        """Supprime les bars des candidats qui ont abandonné une élection."""

        for cand, barset in self.candidates_barsets.items():
            if cand not in self.election.candidates and barset:
                self.series.remove(barset)
                self.candidates_barsets[cand] = None

    def reHighlight(self):
        """Change le highlight d'un bar (si le gagnant a changé)."""
        
        winner = self.election.choose_winner(self.voting_rule)
        if self.winner_barset != self.candidates_barsets[winner]:
            self.winner_barset.setBorderColor(QColor("transparent"))
            self.candidates_barsets[winner].setBorderColor(QColor("black"))
            self.winner_barset = self.candidates_barsets[winner]
