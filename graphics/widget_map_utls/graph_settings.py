from PySide6.QtWidgets import *
from PySide6.QtCore import *
import sys
from sys import argv, exit
import pyqtgraph as pg
import numpy as np

class GraphSettings(QWidget):

    def __init__(self, election, title):
        super().__init__()

        self.graphWidget = pg.PlotWidget()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.graphWidget)
        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setTitle(title)
        self.graphWidget.setXRange(0, 1, padding=0)
        self.graphWidget.setYRange(0, 10, padding=0)
        self.pen = pg.mkPen(color=(255, 0, 0), width=5)
        self.election = election
        mu = 0.5
        sigma = 0.1
        x = []
        y = []
        i = 0
        while i<=1:
            x.append(i)
            y.append((1 / (sigma * np.sqrt(np.pi))) * np.exp(-0.5 * ((i - mu) / sigma) ** 2))
            i=i+0.005
        # plot data: x, y values
        self.graphWidget.plot(x, y, pen=self.pen)

    def updateGraph(self,mu,sigma):
        self.graphWidget.clear()
        x = []
        y = []
        i = 0
        while i<=1:
            x.append(i)
            y.append((1 / (sigma * np.sqrt(np.pi))) * np.exp(-0.5 * ((i - mu) / sigma) ** 2))
            i=i+0.005
        # plot data: x, y values
        self.graphWidget.plot(x, y, pen=self.pen)



