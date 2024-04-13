from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent


class DirectedGraphView(QGraphicsView):
    """Un view qui permet d'afficher les graphes orientés."""

    def __init__(self, scene):
        super().__init__(scene)
        # To suppress warning (MacOS)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
