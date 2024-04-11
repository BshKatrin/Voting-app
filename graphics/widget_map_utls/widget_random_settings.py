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
    """Un widget qui contient des graphiques de loi normale et des sliders pour configurer des paramètres de la génération
    des données."""

    def __init__(self, main_window_size: QSize, parent: Optional[QWidget] = None):
        """Initialiser une instance  d'une élection (pour le partage des données).
        Fixer la taille, le titre et UI.

        Args:
            main_window_size (PySide6.QtCore.QSize): La taille de la fenêtre principale. La taille d'un widget est fixé en fonction 
                de cet argument.
            parent (Optional[PySide6.QtWidgets.QWidget]): Un parent d'un widget. Puisque l'idée est d'afficher le checkbox 
                dans une fenêtre séparée parent est rémis à `None` par défaut.
        """

        super().__init__(parent)

        self.election = Election()

        side_size = 0.6 * min(main_window_size.width(), main_window_size.height())

        self.setWindowTitle("Random generation settings")
        self.setFixedSize(side_size, side_size)

        self.initUI()

    def initUI(self):
        """Initialiser un layout, une zone de défilement et toutes les graphes avec sliders."""

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
