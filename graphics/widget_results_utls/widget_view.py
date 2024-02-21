from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt

from ..settings import GRAPHICS_VIEW_WIDTH, GRAPHICS_VIEW_HEIGHT


class GraphsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        # To suppress warning
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)

        self.resize(GRAPHICS_VIEW_WIDTH, GRAPHICS_VIEW_HEIGHT)

    def closeEvent(self, event):
        self.scene().clear()
        event.accept()
