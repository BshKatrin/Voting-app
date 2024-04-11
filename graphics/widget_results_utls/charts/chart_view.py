from typing import Set

from PySide6.QtCharts import QChartView
from PySide6.QtCore import Qt, Slot, Signal

from electoral_systems import VotingRulesConstants

from .chart_multi_round import ChartMultiRound
from .chart_one_round import ChartOneRound


class ChartView(QChartView):
    """Un view qui affiche des diagrammes à bandes des résultats des règles du vote à un ou plusieurs tours."""

    sig_chart_view_destroying = Signal()
    sig_poll_conducted = Signal(str)

    def __init__(self):
        super().__init__()
        # Suppress warning
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
        self.sig_poll_conducted.connect(self.updateScores)

    def initOneRoundChart(self, one_round_set: Set[str]) -> None:
        """Initialiser des diagrammes à bandes pour des règles du vote à un tour.
        Construire un dictionnaire qui associe une constante d'une règle du vote à son diagramme à bandes.

        Args:
            one_round_set (Set[str]): Un ensemble des constantes des règles du vote à un tour
                dont les diagrammes il faut représenter.
        """

        self.charts_one_rounds = {
            voting_rule: ChartOneRound(voting_rule) for voting_rule in one_round_set
        }

    def initMultiRoundChart(self, multi_round_set: Set[str]) -> None:
        """Initialiser des diagrammes à bandes pour des règles du vote à plusieurs tours.
        Construire un dictionnaire qui associe une constante d'une règle du vote à son diagramme à bandes.

        Args:
            multi_round_set (Set[str]): Un ensemble des constantes des règles du vote à plusieurs tours
                dont les diagrammes il faut représenter.
        """

        self.charts_multi_rounds = {
            voting_rule: ChartMultiRound(voting_rule) for voting_rule in multi_round_set
        }

    @Slot(str)
    def setChartBySig(self, voting_rule: str) -> None:
        """Changer le chart affiché dans un view.

        Args:
            voting_rule (str): Une constante d'une règle du vote dont le diagramme il faut afficher.
        """

        if voting_rule in VotingRulesConstants.MULTI_ROUND:
            chart = self.charts_multi_rounds[voting_rule]
        else:
            chart = self.charts_one_rounds[voting_rule]
        self.setChart(chart)
        self.show()

    @Slot(str)
    def updateScores(self, voting_rule: str) -> None:
        """MAJ des scores des candidats dans une règle du vote `voting_rule`. Utile pour les sondages.

        Args:
            voting_rule (str): Une constante associée à une règle du vote.
        """

        self.charts_one_rounds[voting_rule].updateData()

    @Slot()
    def delete_children(self) -> None:
        """Supprimer tous les charts qui ont été initialisés"""

        self.setChart(None)  # because setChart takes ownership
        for multi_chart in self.charts_multi_rounds.values():
            multi_chart.deleteLater()
        for one_chart in self.charts_one_rounds.values():
            one_chart.deleteLater()
