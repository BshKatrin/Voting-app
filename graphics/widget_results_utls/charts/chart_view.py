from PySide6.QtCharts import QChartView
from PySide6.QtCore import Qt, Slot, Signal

from electoral_systems.voting_rules.constants import *

from .chart_multi_round import ChartMultiRound
from .chart_one_round import ChartOneRound


class ChartView(QChartView):
    sig_chart_view_destroying = Signal()

    def __init__(self):
        super().__init__()
        # Suppress warning
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)

    def initOneRoundChart(self, oneRoundSet):
        self.charts_one_rounds = {
            voting_rule: ChartOneRound(voting_rule) for voting_rule in oneRoundSet
        }

    def initMultiRoundChart(self, multiRoundSet):
        self.charts_multi_rounds = {
            voting_rule: ChartMultiRound(voting_rule) for voting_rule in multiRoundSet
        }

    @Slot(str)
    def setChartBySig(self, voting_rule):
        if voting_rule in {EXHAUSTIVE_BALLOT, PLURALITY_2_ROUNDS}:
            chart = self.charts_multi_rounds[voting_rule]
        else:
            chart = self.charts_one_rounds[voting_rule]
        self.setChart(chart)
        self.show()

    @Slot()
    def delete_children(self):
        self.setChart(None)  # because setChart takes ownership
        # self.chart_one_round.deleteLater()
        for multi_chart in self.charts_multi_rounds.values():
            multi_chart.deleteLater()
        for one_chart in self.charts_one_rounds.values():
            one_chart.deleteLater()
