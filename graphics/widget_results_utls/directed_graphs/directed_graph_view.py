from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent


class DirectedGraphView(QGraphicsView):
    """A view which displays oriented graphs."""

    def __init__(self, scene:QGraphicsScene):
        """
        Args:
            scene (PySide6.QtWidgets.QGraphicsScene): A scene to show.
        """
        
        super().__init__(scene)
        # To suppress warning (MacOS)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
