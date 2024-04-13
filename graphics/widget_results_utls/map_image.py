from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt, Signal, QSize

from electoral_systems import Election
from ..widget_map_utls import QuadrantMap


class MapImage(QWidget):
    """Un widget qui affiche la carte politique non interactive (i.e. qui ne répond pas au cliques du souris)."""

    closed = Signal()
    """Un signal émis lorsque le widget est fermé."""

    def __init__(self, size, parent: QWidget = None):
        """Initialise une instance d'élection (pour le partage des données).

        Args:
            size (PySide6.QtCore.QSize): La taille d'un widget.
            parent (PySide6.QtWidgets.QWidget): Un parent d'un widget. Puisque l'idée est d'afficher le checkbox 
                dans une fenêtre séparée parent est remis à `None` par défaut.
        """

        super().__init__(parent)
        self.election = Election()
        self.setGeometry(0, 0, size.width(), size.height())
        self.initImage()
        self.disableMouseEvent()

    def initImage(self) -> None:
        """Initialise la layout, la carte politique."""

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.quadrant_map = QuadrantMap(0.95, self)
        if self.election.liquid_democracy_activated:
            self.quadrant_map.draw_delegations = True

        self.layout.addWidget(self.quadrant_map, 0, Qt.AlignVCenter | Qt.AlignHCenter)

    def update(self) -> None:
        """Redessine la carte politique."""

        self.quadrant_map.update()

    def disableMouseEvent(self) -> None:
        """Désactive l'interaction avec la souris."""

        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def closeEvent(self, event: QCloseEvent):
        """Redéfinition d'un `closeEvent`. Ferme le widget (mais ne le supprime pas). Émet le signal `closed`."""

        self.closed.emit()
        self.close()
        event.accept()
