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
    """A class representing the widget with the configuration of a single data generation parameter."""

    def __init__(self, parent: QWidget, title: str, type: str, graph_type: int):
        """Initialize an instance of the election (for data sharing).
        Initialize graphic (if necessary) and one or more sliders.

        Args:
            parent (PySide6.QtWidgets.QWidget): Widget's parent.
            title (str): A name of the parameter to configure (UI version).
            type (str): A constant associated to the parameter type (e.g. economical, social).
            graph_type (int): A type of graphic to initialize.
        """

        super().__init__(parent)

        self.election = Election()
        self.type = type

        self.graph_size = parent.size() * 0.8

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Initialize graphics (by type)
        match graph_type:
            case RandomConstants.LINEAR:
                self.initPlot(title)
                self.setFixedSize(self.parent().size() * 0.8)
                self.initLinearInput()
            case RandomConstants.GAUSS:
                self.initPlot(title)
                self.setFixedSize(self.parent().size() * 0.8)
                self.initGaussInput()
            case RandomConstants.SLIDER:
                self.initDistInput(title)
                self.setFixedWidth(self.parent().width() * 0.8)

    def initLinearInput(self) -> None:
        """Initialize sliders for linear graphic (parameter `orientation`)."""

        sub_layout = QGridLayout()

        self.orientation_result = QLabel("", self)

        self.slider_orientation = QSlider(Qt.Horizontal, self)
        self.slider_orientation.valueChanged.connect(self.updateOrientation)
        self.slider_orientation.setValue(self.election.generation_constants[self.type])

        min, max = RandomConstants.VALUES_MIN_MAX[self.type]
        self.slider_orientation.setRange(min, max)
        self.slider_orientation.setTickInterval(1)

        sub_layout.addWidget(self.slider_orientation, 0, 1, 1, 2)
        sub_layout.addWidget(
            self.orientation_result, 0, 3, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(sub_layout)

    def initGaussInput(self) -> None:
        """Initialize sliders for graphic of normal distribution (parameters based on the normal distribution)."""

        sub_layout = QGridLayout()

        mu_label = QLabel("Mu", self)
        sigma_label = QLabel("Sigma", self)

        mu, sigma = self.election.generation_constants[self.type]
        self.mu_result_label = QLabel(f"{mu:.2f}", self)
        self.sigma_result_label = QLabel(f"{sigma:.2f}", self)

        self.mu_slider = QSlider(Qt.Horizontal, self)
        self.sigma_slider = QSlider(Qt.Horizontal, self)

        constants = self.election.generation_constants[self.type]

        self.mu_slider.valueChanged.connect(self.updateMuConstant)
        self.sigma_slider.valueChanged.connect(self.updateSigmaConstant)

        self.mu_slider.setValue(constants[0] * 100)
        self.sigma_slider.setValue(constants[1] * 100)

        min, max = RandomConstants.VALUES_MIN_MAX[self.type]
        self.mu_slider.setRange(min, max)
        self.sigma_slider.setRange(0, 100)

        sub_layout.addWidget(
            mu_label,
            0,
            0,
        )
        sub_layout.addWidget(self.mu_slider, 0, 1, 1, 2)
        sub_layout.addWidget(
            self.mu_result_label, 0, 3, alignment=Qt.AlignmentFlag.AlignRight
        )

        sub_layout.addWidget(sigma_label, 1, 0)
        sub_layout.addWidget(self.sigma_slider, 1, 1, 1, 2)
        sub_layout.addWidget(
            self.sigma_result_label, 1, 3, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(sub_layout)

    def initPlot(self, title: str) -> None:
        """Initialize a canvas for a graphic.

        Args:
            title (str): A name of the parameter to configure (UI version). 
        """

        self.graphWidget = PlotWidget()
        # Suppress warning (MacOS)
        self.graphWidget.viewport().setAttribute(
            Qt.WidgetAttribute.WA_AcceptTouchEvents, False
        )
        self.graphWidget.setAntialiasing(True)
        # Desactivate zoom
        self.graphWidget.setMouseEnabled(x=False, y=False)

        self.graphWidget.setBackground("w")
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setTitle(title)
        self.pen = mkPen(color=(255, 0, 0), width=5)

        self.layout.addWidget(self.graphWidget, 0)

    def initDistInput(self, title: str) -> None:
        """Initialize sliders for parameters without graphic. (parameter `travel_dist`).

        Args:
            title (str): A name of the parameter to configure (UI version).
        """

        sub_layout = QGridLayout()
        self.dist_title = QLabel(title, self)
        self.dist_title.setStyleSheet("font-weight: bold")
        current_value = self.election.generation_constants[self.type]
        self.dist_result = QLabel(f"{current_value:.2f}", self)
        self.dist_slider = QSlider(Qt.Horizontal, self)

        min, max = RandomConstants.VALUES_MIN_MAX[self.type]
        self.dist_slider.setRange(min, max)
        self.dist_slider.setValue(int(current_value * 100))
        self.dist_slider.valueChanged.connect(self.updateDistUpdate)

        sub_layout.addWidget(self.dist_title, 0, 1)
        sub_layout.addWidget(self.dist_slider, 1, 0, 1, 2)
        sub_layout.addWidget(
            self.dist_result, 1, 2, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(sub_layout)

    @Slot(int)
    def updateMuConstant(self, value: int) -> None:
        """Change the mean value of the normal distribution. Called if a connected slider has been moved. 
        Redraw graphic with changed mean. Update the value of this parameter in the election.

        Args:
            value (int): A value on a slider. *Will be divided by 100*.
        """

        _, old_sigma = self.election.generation_constants[self.type]
        new_mu = value / 100
        self.election.generation_constants[self.type] = (
            new_mu,
            old_sigma,
        )
        self.mu_result_label.setText(f"{new_mu:.2f}")
        x_min, x_max = RandomConstants.VALUES_MIN_MAX[self.type]
        self.updateGraphGauss(new_mu, old_sigma, x_min / 100 - 0.15, x_max / 100 + 0.15)

    @Slot(int)
    def updateSigmaConstant(self, value: int) -> None:
        """Change the variance value of the normal distribution. Called if a connected slider has been moved. 
        Redraw graphic with changed variance. Update the value of this parameter in the election.

        Args:
            value (int): A value on a slider. *Will be divided by 100*.
        """

        old_mu, _ = self.election.generation_constants[self.type]
        new_sigma = value / 100
        self.election.generation_constants[self.type] = (
            old_mu,
            new_sigma,
        )
        self.sigma_result_label.setText(f"{new_sigma:.2f}")
        x_min, x_max = RandomConstants.VALUES_MIN_MAX[self.type]
        self.updateGraphGauss(old_mu, new_sigma, x_min / 100 - 0.15, x_max / 100 + 0.15)

    @Slot(int)
    def updateOrientation(self, value: int) -> None:
        """Change value line's coefficient directeur. Called if the corresponding slider has been moved.
        Redraw graphic on a line. Update the value of this parameter in the election.

        Args:
            value (int): A value on a slider. No arithmetical operation will be performed.
        """

        self.election.generation_constants[self.type] = value
        self.orientation_result.setText(str(value))

        self.updateGraphAffine(value)

    @Slot(int)
    def updateDistUpdate(self, value: int) -> None:
        """Change the value of candidate's `travel_dist`. Update the value of this parameter in the election.

        Args:
            value (int): A value on a slider. Will be divised by 100.
        """

        self.election.generation_constants[self.type] = value / 100
        self.dist_result.setText(f"{value / 100:.2f}")

    def updateGraphGauss(self, mu: float, sigma: float, x_min: float, x_max: float) -> None:
        """Redraw graphic of the normal distribution.

        Args:
            mu (float): The mean of the normal distribution.
            sigma (float): The variance of the normal distribution. A strictly positive float.
            x_min (float): The minimum value of the X-axis.
            x_max (float): The maximum value of the X-axis.
        """

        self.graphWidget.clear()
        self.graphWidget.setXRange(x_min, x_max, padding=0)
        self.graphWidget.setYRange(0, 3, padding=0)

        step = 0.005
        x = arange(start=-1, stop=1 + step, step=step, dtype=float)
        y = array([self.calculateYGauss(i, mu, sigma) for i in x])

        # plot data: x, y values
        self.graphWidget.plot(x, y, pen=self.pen)

    def updateGraphAffine(self, slope: float) -> None:
        """Redraw graphic of the line. It's coefficient libre is 0.

        Args:
            slope (float): Le coefficient directeur of the line.
        """

        self.graphWidget.clear()
        self.graphWidget.setXRange(-1, 1, padding=0)
        self.graphWidget.setYRange(-1, 1, padding=0)

        step = 0.05
        x = arange(start=-1, stop=1 + step, step=step, dtype=float)
        y = array([self.calculateYLinear(i, slope) for i in x])

        self.graphWidget.plot(x, y, pen=self.pen)

    def calculateYGauss(self, i: float, mu: float, sigma: float) -> float:
        """Calculate the value of *y* on *x* (normal distribution graphic).

        Args:
            i (float): The value of *x*.
            mu (float): The mean of the normal distribution.
            sigma (float): The variance of the normal distribution. A strictly positive float.
        """

        return (1 / ((sigma + 0.01) * sqrt(pi))) * exp(
            -0.5 * ((i - mu) / (sigma + 0.01)) ** 2
        )

    def calculateYLinear(self, i: float, slope: float) -> float:
        """Calculate the value of *y* on *x* (linear graphic).

        Args:
            i (float): The value of *x*. 
            slope (float): Le coefficient directeur.
        """

        return slope * i
