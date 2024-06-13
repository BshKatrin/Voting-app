from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt, Signal, QSize

from electoral_systems import Election
from ..widget_map_utls import QuadrantMap


class MapImage(QWidget):
    """A widget which represents the non-interactive political map."""

    closed = Signal()
    """A signal emitted if the widget has been closed."""

    def __init__(self, size, parent: QWidget = None):
        """Initialize an instance of the election (for data sharing).

        Args:
            size (PySide6.QtCore.QSize): Widget's size.
            parent (PySide6.QtWidgets.QWidget): Widget's parent. Default = `None`.
        """

        super().__init__(parent)
        self.election = Election()
        self.setGeometry(0, 0, size.width(), size.height())
        self.initImage()
        self.disableMouseEvent()

    def initImage(self) -> None:
        """Initialize the layout, the political map."""

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.quadrant_map = QuadrantMap(0.95, self)
        if self.election.liquid_democracy_activated:
            self.quadrant_map.draw_delegations = True

        self.layout.addWidget(self.quadrant_map, 0, Qt.AlignVCenter | Qt.AlignHCenter)

    def update(self) -> None:
        """Redraw the political map."""

        self.quadrant_map.update()

    def disableMouseEvent(self) -> None:
        """Desactivate the interaction with the mouse."""

        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def closeEvent(self, event: QCloseEvent):
        """Redefinition of the `closeEvent`. Close the widget (but not delete it). Emit the signal `closed`."""

        self.closed.emit()
        self.close()
        event.accept()
