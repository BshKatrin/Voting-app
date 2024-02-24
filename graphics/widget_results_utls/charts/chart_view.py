from PySide6.QtCharts import QChartView
from PySide6.QtCore import Qt, Slot

from ...settings import GRAPHICS_VIEW_WIDTH, GRAPHICS_VIEW_HEIGHT
from electoral_systems.voting_rules.constants import *

from .chart_multi_round import ChartMultiRound
from .chart_one_round import ChartOneRound


class ChartView(QChartView):
    def __init__(self):
        super().__init__()
        # Suppress warning
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
        self.resize(GRAPHICS_VIEW_WIDTH, GRAPHICS_VIEW_HEIGHT)

    def initOneRoundChart(self, oneRoundSet):
        self.chart_one_round = ChartOneRound(oneRoundSet)

    def initMultiRoundChart(self, multiRoundSet):
        self.charts_multi_rounds = {
            voting_rule: ChartMultiRound(voting_rule) for voting_rule in multiRoundSet
        }

    @Slot(str)
    def setChartBySig(self, voting_rule):
        if voting_rule in {EXHAUSTIVE_BALLOT, PLURALITY_2_ROUNDS}:
            chart = self.charts_multi_rounds[voting_rule]
            self.setChart(chart)
        else:
            self.setChart(self.chart_one_round)
        self.show()
