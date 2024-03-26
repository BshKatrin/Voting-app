from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from pyqtgraph import PlotWidget, mkPen

from numpy import arange, array, sqrt, pi, exp
from electoral_systems import Election


class GraphSettings(QWidget):

    def __init__(self, parent, title):
        super().__init__(parent)

        self.election = Election()

        self.initPlot(title)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.graphWidget)

    def initPlot(self, title):
        self.graphWidget = PlotWidget()
        # Suppress warning (MacOS)
        self.graphWidget.viewport().setAttribute(
            Qt.WidgetAttribute.WA_AcceptTouchEvents, False
        )
        self.graphWidget.setAntialiasing(True)
        # Deactivate zoom
        self.graphWidget.setMouseEnabled(x=False, y=False)

        self.graphWidget.setBackground("w")
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setTitle(title)
        self.pen = mkPen(color=(255, 0, 0), width=5)

    def _calculateYGauss(self, i, mu, sigma):
        return (1 / ((sigma + 0.01) * sqrt(pi))) * exp(
            -0.5 * ((i - mu) / (sigma + 0.01)) ** 2
        )

    def updateGraphGauss(self, mu, sigma):
        self.graphWidget.clear()
        self.graphWidget.setXRange(0, 1, padding=0)
        self.graphWidget.setYRange(0, 10, padding=0)

        step = 0.005
        x = arange(start=0, stop=1 + step, step=step, dtype=float)
        y = array([self._calculateYGauss(i, mu, sigma) for i in x])

        # plot data: x, y values
        self.graphWidget.plot(x, y, pen=self.pen)

    def _calculateYAffine(self, i, coeffdir, mu):
        return (coeffdir * i) + mu

    def updateGraphAffine(self, coeffdir, mu):
        self.graphWidget.clear()
        self.graphWidget.setXRange(-1, 1, padding=0)
        self.graphWidget.setYRange(-1, 1, padding=0)

        step = 0.005
        x = arange(start=-1, stop=1 + step, step=0.005)
        y = array([self._calculateYAffine(i, coeffdir, mu) for i in x])

        self.graphWidget.plot(x, y, pen=self.pen)
