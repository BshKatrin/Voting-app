from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QLabel,
    QSlider,
    QGridLayout,
    QVBoxLayout,
)
from PySide6.QtCore import Qt

from .graph_settings import GraphSettings

from electoral_systems import Election
from electoral_systems import RandomConstants


class WidgetSettings(QWidget):

    def __init__(self, window_size, quadrant_map_size, parent=None):
        super().__init__(parent)

        self.election = Election()

        side_size = 0.6 * min(window_size.width(), window_size.height())
        # Suffit car quadrant map est carre
        self.quadrant_map_size = quadrant_map_size.width()
        self.setWindowTitle("Random generation settings")
        # configuration taille du window
        self.setFixedSize(side_size, side_size)

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        scrollArea = QScrollArea()
        main_layout.addWidget(scrollArea)

        scroll_widget = QWidget()

        layout = QVBoxLayout()
        scroll_widget.setLayout(layout)
        for type, title in RandomConstants.UI.items():
            graph_type = RandomConstants.GRAPH_TYPE[type]
            graph = GraphSettings(self, title, type, graph_type, self.quadrant_map_size)

            layout.addWidget(graph)

        scrollArea.setWidget(scroll_widget)
