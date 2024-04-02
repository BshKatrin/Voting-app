from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QCloseEvent, QPixmap
from PySide6.QtCore import Signal, Slot
from PySide6.QtCore import Qt

from ..widget_map_utls import QuadrantMap


class MapImage(QWidget):
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.initImage(image_path)
        self.initImage()
        self.disableMouseEvent()

    def initImage(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setGeometry(0, 0, 600, 600)

        self.quadrant_map = QuadrantMap(0.95, self)

        self.layout.addWidget(self.quadrant_map, 0, Qt.AlignVCenter | Qt.AlignHCenter)

    def update(self):
        self.quadrant_map.update()

    def disableMouseEvent(self):
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    # def initImage(self, image_path):
    #     self.layout = QVBoxLayout()
    #     self.setLayout(self.layout)

    #     self.pixmap = QPixmap(image_path, "PNG")

    #     if self.pixmap.isNull():
    #         print("Error : loading quadrant map image")
    #         return

    #     self.setGeometry(
    #         100, 100, self.pixmap.width() * 1.05, self.pixmap.height() * 1.05
    #     )
    #     self.image_label = QLabel(self)
    #     self.image_label.setPixmap(self.pixmap)
    #     self.layout.addWidget(self.image_label, 0, Qt.AlignVCenter | Qt.AlignHCenter)

    def closeEvent(self, event: QCloseEvent):
        self.closed.emit()
        self.close()
        event.accept()
