from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt

from electoral_systems import Election
from ..widget_map_utls import QuadrantMap


class MapImage(QWidget):
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.initImage(image_path)
        self.election = Election()
        self.initImage()
        self.disableMouseEvent()

    def initImage(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setGeometry(0, 0, 600, 600)

        self.quadrant_map = QuadrantMap(0.95, self)
        if self.election.liquid_democracy_activated:
            self.quadrant_map.draw_delegations = True

        self.layout.addWidget(self.quadrant_map, 0, Qt.AlignVCenter | Qt.AlignHCenter)

    def update(self):
        self.quadrant_map.update()

    def disableMouseEvent(self):
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def closeEvent(self, event: QCloseEvent):
        self.closed.emit()
        self.close()
        event.accept()
