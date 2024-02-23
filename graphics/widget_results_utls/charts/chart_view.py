from PySide6.QtCharts import QChartView
from PySide6.QtCore import Qt
from ...settings import GRAPHICS_VIEW_WIDTH, GRAPHICS_VIEW_HEIGHT


class ChartView(QChartView):
    def __init__(self, chart):
        super().__init__(chart)
        # Suppress warning
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
        self.resize(GRAPHICS_VIEW_WIDTH, GRAPHICS_VIEW_HEIGHT)
