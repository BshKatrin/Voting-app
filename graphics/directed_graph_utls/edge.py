from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsSimpleTextItem
from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import Qt


# To connect nodes
class Edge(QGraphicsPathItem):
    def __init__(self, painter_path, start_point, end_point):
        super().__init__(painter_path, None)

        self.setPen(QPen(Qt.black, 2))
        self.start_point = start_point
        self.end_point = end_point
        self.path = painter_path

        self.initUI()

    def initUI(self):
        self.path.moveTo(self.start_pos)
        self.path.lineTo(self.end_pos)

    def setWeight(self, weight):
        print("setWeight")
        self.text = QGraphicsSimpleTextItem(parent=self)
        self.text.setText(str(weight))
        self.text.setPos((self.start_point + self.end_point) / 2)
    
        def calculateArrowHead(self, start_pos, end_pos):
        arrowSize = 20
        # Calculate angle, -y since y-axe is inversed
        angle = atan2(
            -(start_pos.y() - end_pos.y()),
            start_pos.x() - end_pos.x(),
        )
        # Calculate offset for each arrow point
        # From polar to normal, inversing axes since we need counter-clockwize angle
        offsetOne = QPointF(
            sin(angle + pi / 3) * arrowSize, cos(angle + pi / 3) * arrowSize
        )
        offsetTwo = QPointF(
            sin(angle + pi * 2 / 3) * arrowSize,
            cos(angle + pi * 2 / 3) * arrowSize,
        )

        pointOne = end_pos + offsetOne
        pointTwo = end_pos + offsetTwo
        return QPolygonF([pointOne, pointTwo, end_pos])