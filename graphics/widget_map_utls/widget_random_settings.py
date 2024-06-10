from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QVBoxLayout,
)

from PySide6.QtCore import Qt, QSize
from .graph_settings import GraphSettings

from electoral_systems import Election
from electoral_systems import RandomConstants


class WidgetRandomSettings(QWidget):
    """A class representing the widget with all graphics of the normal distribution
    and sliders to configure the parameters of data generation."""

    def __init__(self, main_window_size: QSize, parent: Optional[QWidget] = None):
        """Initialize an instance of the election (for data sharing).
        Initialize sliders and graphics for each data generation parameter.


        Args:
            main_window_size (PySide6.QtCore.QSize): A size of the main window. A size of the widget will be determined by this arg.
            parent (Optional[PySide6.QtWidgets.QWidget]): Widget's parent. The idea is to to show this widget
                in a separate window so the default is `None`.
        """

        super().__init__(parent)

        self.election = Election()

        side_size = 0.6 * min(main_window_size.width(), main_window_size.height())

        self.setWindowTitle("Random generation settings")
        self.setFixedSize(side_size, side_size)

        self.initUI()

    def initUI(self):
        """Initialize the layout, scrolling zone, all graphics with sliders."""

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
