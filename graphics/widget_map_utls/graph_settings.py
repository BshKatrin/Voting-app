from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSlider,
    QGridLayout,
)
from PySide6.QtCore import Qt, Slot

from pyqtgraph import PlotWidget, mkPen

from numpy import arange, array, sqrt, pi, exp
from electoral_systems import Election, RandomConstants


class GraphSettings(QWidget):

    def __init__(self, parent, title, type, graph_type, quadrant_map_size):
        super().__init__(parent)

        self.election = Election()

        self.type = type

        self.map_size = quadrant_map_size

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.initPlot(title)
        self.layout.addWidget(self.graphWidget)

        # Init graphs based on a type
        match graph_type:
            case RandomConstants.LINEAR:
                self.initLinearInput()
            case RandomConstants.GAUSS:
                self.initGaussInput()

    @Slot(float)
    def updateMuConstant(self, value):
        _, old_sigma = self.election.generation_constants[self.type]
        new_mu = value / 100
        self.election.generation_constants[self.type] = (
            new_mu,
            old_sigma,
        )
        self.mu_result_label.setText(f"{new_mu:.2f}")
        self.updateGraphGauss(new_mu, old_sigma)

    @Slot(float)
    def updateSigmaConstant(self, value):
        old_mu, _ = self.election.generation_constants[self.type]
        new_sigma = value / 100
        self.election.generation_constants[self.type] = (
            old_mu,
            new_sigma,
        )
        self.sigma_result_label.setText(f"{new_sigma:.2f}")
        self.updateGraphGauss(old_mu, new_sigma)

    @Slot(float)
    def updateOrientation(self, value):
        self.election.generation_constants[self.type] = value
        self.orientation_result.setText(str(value))

        mu = self.election.generation_constants[RandomConstants.SOCIAL][0]
        self.updateGraphAffine(value, mu)

    def initLinearInput(self):
        sub_layout = QGridLayout()
        self.orientation_label = QLabel("Orientation", self)

        self.orientation_result = QLabel("", self)

        self.slider_orientation = QSlider(Qt.Horizontal, self)
        self.slider_orientation.valueChanged.connect(self.updateOrientation)
        self.slider_orientation.setValue(self.election.generation_constants[self.type])
        self.slider_orientation.setRange(-1, 1)
        self.slider_orientation.setTickInterval(1)

        sub_layout.addWidget(self.orientation_label, 0, 0)
        sub_layout.addWidget(self.slider_orientation, 0, 1, 1, 2)
        sub_layout.addWidget(self.orientation_result, 0, 3)

        self.layout.addLayout(sub_layout)

    def initGaussInput(self):
        # Grid()
        sub_layout = QGridLayout()

        mu_label = QLabel("Mu", self)
        sigma_label = QLabel("Sigma", self)

        self.mu_result_label = QLabel("", self)
        self.sigma_result_label = QLabel("", self)

        self.mu_slider = QSlider(Qt.Horizontal, self)
        self.sigma_slider = QSlider(Qt.Horizontal, self)

        constants = self.election.generation_constants[self.type]

        self.mu_slider.valueChanged.connect(self.updateMuConstant)
        self.sigma_slider.valueChanged.connect(self.updateSigmaConstant)

        self.mu_slider.setValue(constants[0] * 100)
        self.sigma_slider.setValue(constants[1] * 100)

        self.mu_slider.setRange(-85, 85)
        self.sigma_slider.setRange(0, 100)

        sub_layout.addWidget(mu_label, 0, 0)
        sub_layout.addWidget(self.mu_slider, 0, 1, 1, 2)
        sub_layout.addWidget(self.mu_result_label, 0, 3)

        sub_layout.addWidget(sigma_label, 1, 0)
        sub_layout.addWidget(self.sigma_slider, 1, 1, 1, 2)
        sub_layout.addWidget(self.sigma_result_label, 1, 3)

        self.layout.addLayout(sub_layout)

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
        self.graphWidget.setXRange(-1, 1, padding=0)
        self.graphWidget.setYRange(0, 3, padding=0)

        step = 0.005
        x = arange(start=-1, stop=1 + step, step=step, dtype=float)
        y = array([self._calculateYGauss(i, mu, sigma) for i in x])

        # plot data: x, y values
        self.graphWidget.plot(x, y, pen=self.pen)

    def _calculateYLinear(self, i, slope, mu):
        return (slope * i) + mu

    def updateGraphAffine(self, slope, mu):
        self.graphWidget.clear()
        self.graphWidget.setXRange(-1, 1, padding=0)
        self.graphWidget.setYRange(-1, 1, padding=0)

        step = 0.05
        x = arange(start=-1, stop=1 + step, step=step, dtype=float)
        y = array([self._calculateYLinear(i, slope, mu) for i in x])

        self.graphWidget.plot(x, y, pen=self.pen)
