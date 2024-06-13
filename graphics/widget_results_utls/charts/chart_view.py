from typing import Set

from PySide6.QtCharts import QChartView
from PySide6.QtCore import Qt, Slot, Signal

from electoral_systems import VotingRulesConstants

from .chart_multi_round import ChartMultiRound
from .chart_one_round import ChartOneRound


class ChartView(QChartView):
    """A view to display charts with results of the one & multi-round voting rules."""

    sig_chart_view_destroying = Signal()
    sig_poll_conducted = Signal(str)

    def __init__(self):
        super().__init__()
        # Suppress warning
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
        self.sig_poll_conducted.connect(self.updateScores)

    def initOneRoundChart(self, one_round_set: Set[str]) -> None:
        """Initialize charts of one round voting rules.
            Initialize and fill a dictionary which associates a constant related to the voting rule and its chart.

        Args:
            one_round_set (Set[str]): A set of constants related to one round voting rules whose charts should be initialized. 
        """

        self.charts_one_rounds = {
            voting_rule: ChartOneRound(voting_rule) for voting_rule in one_round_set
        }

    def initMultiRoundChart(self, multi_round_set: Set[str]) -> None:
        """Initialize charts of multi-round voting rules.
            Initialize and fill a dictionary which associates a constant related to the voting rule and its chart.

        Args:
            multi_round_set (Set[str]): A set of constants related to multi-round voting rules whose charts should be initialized. 
        """

        self.charts_multi_rounds = {
            voting_rule: ChartMultiRound(voting_rule) for voting_rule in multi_round_set
        }

    @Slot(str)
    def setChartBySig(self, voting_rule: str) -> None:
        """Change the chart displayd in the view.
        Args:
            voting_rule (str): A constant related to the voting rule whose chart should be shown.
        """

        if voting_rule in VotingRulesConstants.MULTI_ROUND:
            chart = self.charts_multi_rounds[voting_rule]
        else:
            chart = self.charts_one_rounds[voting_rule]
        self.setChart(chart)
        self.show()

    @Slot(str)
    def updateScores(self, voting_rule: str) -> None:
        """Update candidates' scores in the given voting rule. Useful for polls.

        Args:
            voting_rule (str): A constant related to the voting rule.
        """

        self.charts_one_rounds[voting_rule].updateData()

    @Slot()
    def delete_children(self) -> None:
        """Delete all initialized charts."""

        self.setChart(None)  # because setChart takes ownership
        for multi_chart in self.charts_multi_rounds.values():
            multi_chart.deleteLater()
        for one_chart in self.charts_one_rounds.values():
            one_chart.deleteLater()
