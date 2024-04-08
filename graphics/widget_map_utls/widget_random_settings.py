from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QVBoxLayout,
)

from PySide6.QtCore import Qt
from .graph_settings import GraphSettings

from electoral_systems import Election
from electoral_systems import RandomConstants


class WidgetRandomSettings(QWidget):

    def __init__(self, main_window_size, parent=None):
        super().__init__(parent)

        self.election = Election()

        side_size = 0.6 * min(main_window_size.width(), main_window_size.height())

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
            graph = GraphSettings(self, title, type, graph_type)

            layout.addWidget(graph, 0, alignment=Qt.AlignmentFlag.AlignHCenter)

        scrollArea.setWidget(scroll_widget)
