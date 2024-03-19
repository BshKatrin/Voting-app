from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QCloseEvent, QPixmap
from PySide6.QtCore import Signal, Slot
from PySide6.QtCore import Qt


class MapImage(QWidget):
    closed = Signal()

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.initImage(image_path)

    def initImage(self, image_path):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.pixmap = QPixmap(image_path, "PNG")

        if self.pixmap.isNull():
            print("Error : loading quadrant map image")
            return

        self.setGeometry(
            100, 100, self.pixmap.width() * 1.05, self.pixmap.height() * 1.05
        )
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.pixmap)
        self.layout.addWidget(self.image_label, 0, Qt.AlignVCenter | Qt.AlignHCenter)

    def closeEvent(self, event: QCloseEvent):
        self.closed.emit()
        self.close()
        event.accept()
