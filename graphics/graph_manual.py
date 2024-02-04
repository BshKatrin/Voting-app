from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from .graph import Graph


class GraphManual(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.initUI()

    def initUI(self):
        self.graph = Graph(parent=self)
        self.layout.addWidget(self.graph)
