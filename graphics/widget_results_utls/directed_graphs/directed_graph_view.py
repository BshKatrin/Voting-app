from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt


class DirectedGraphView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        # To suppress warning
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)

    def closeEvent(self, event):
        self.scene().clear()
        event.accept()
