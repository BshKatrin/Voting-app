from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QTransform, QColor, QPaintEvent, QMouseEvent
from PySide6.QtCore import Qt, QPointF, QPoint, QSize

from numpy import clip
from numpy.random import normal
from electoral_systems import Election, RandomConstants

# For docs generation only
__pdoc__ = {
    'normal':False
}

class QuadrantMap(QWidget):
    """A widget which represents the political map. The political map is drawn with `PySide6.QtGui.QPainter`."""

    def __init__(self, size_proportion: float, parent: QWidget):
        """Initialize an instance of the election (for data sharing).

        Args:
            size_proportion (float): A proportion of the parent-widget's size.
                The size of the widget will be fixed based on this proportion. 
            parent (PySide6.QtWidgets.QWidget): Widget's parent.
        """

        super().__init__(parent)

        self.election = Election()
        self.draw_delegations = False

        side_size = min(parent.width(), parent.height())
        self.setFixedSize(size_proportion * side_size, size_proportion * side_size)

        self.setTransformation()
        self.initUI()

    def setTransformation(self) -> None:
        """Initialize (but not applied) computer coordinates transformation.
            Goal: have the cartesian coordinate system."""

        self.transform = QTransform()
        # Order matters !
        # Flip Y-axis
        self.transform.scale(1, -1)
        # Move center
        self.transform.translate(self.width() / 2, -self.height() / 2)

    def initUI(self):
        """Initialize the layout. Change background color to white. Initialize the step to draw the grid."""

        self.layout = QVBoxLayout(self)
        self.setPallete()

        self.grid_step = 20
        self.text_box_active = False

    def setPallete(self) -> None:
        """Change background color to white."""

        self.setAutoFillBackground(True)
        pallete = self.palette()
        pallete.setColor(self.backgroundRole(), QColor(255, 255, 255))
        self.setPalette(pallete)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Redefine `paintEvent` by default. Draw the grid, X and Y axes. Apply the coordinates transformation.
            Draw points corresponding to existing electors and candidates."""

        painter = QPainter(self)
        self.drawGrid(painter)
        self.drawAxes(painter)
        self.drawAxisLabels(painter)

        painter.setTransform(self.transform)

        if self.draw_delegations:
            self.drawElectorsDelegation(painter)
        else:
            self.drawPoints(painter)

    def drawGrid(self, painter: QPainter) -> None:
        """Draw the grid.

        Args:
            painter (PySide6.QtGui.QPainter): An initialized painter.
        """

        # Pale gray color
        pen = QPen(QColor(220, 220, 220))
        painter.setPen(pen)
        # nb_lines = nb_rows = nb_cols
        nb_lines = self.width() // self.grid_step

        for row in range(1, nb_lines + 1):
            # Vertical lines 
            painter.drawLine(
                row * self.grid_step, 0, row * self.grid_step, self.height()
            )
            # Horizontal lines
            painter.drawLine(
                0, row * self.grid_step, self.width(), row * self.grid_step
            )

    def drawAxes(self, painter: QPainter) -> None:
        """Draw X and Y axes. 

        Args:
            painter (PySide6.QtGui.QPainter): An initialized painter.
        """

        # Black color
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)

        # Width = height
        central_line = self.width() // self.grid_step / 2
        painter.setPen(pen)
        # X-axes
        painter.drawLine(
            0,
            central_line * self.grid_step,
            self.width(),
            central_line * self.grid_step,
        )
        # Y-axes
        painter.drawLine(
            central_line * self.grid_step,
            0,
            central_line * self.grid_step,
            self.height(),
        )

    def drawAxisLabels(self, painter: QPainter) -> None:
        """Draw the axes labels.

        Args:
            painter (PySide6.QtGui.QPainter): An initialized painter.
        """

        # Black color
        pen = QPen(QColor(0, 0, 0))
        painter.setPen(pen)
        # QFont to define font properties
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        # Apply font properties to the pens
        painter.setFont(font)

        painter.drawText(self.width() - 40, self.height() / 2 + 30, "Right")
        painter.drawText(self.width() / 2 - 85, 20, "Autoritarian")
        painter.drawText(self.width() / 150, self.height() / 2 + 30, "Left")
        painter.drawText(self.width() / 2 - 60, self.height() - 10, "Liberal")

    def drawElectors(self, painter: QPainter) -> None:
        """Draw the points corresponding to the existing electors (without liquid democracy).

        Args:
            painter (PySide6.QtGui.QPainter): An initialized painter.
        """

        # Standard blue color
        pen = QPen(QColor(0, 0, 255))
        pen.setWidth(4)
        painter.setPen(pen)
        for elector in self.election.electors:
            painter.drawPoint(self.scaleCoordinates(elector.position))

    def drawCandidates(self, painter: QPainter) -> None:
        """Draw the points to the existing candidates.

        Args:
            painter (PySide6.QtGui.QPainter): An initialized painter.
        """

        # Standard red color 
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(4)
        painter.setPen(pen)
        for candidate in self.election.candidates:
            fst_name, lst_name = candidate.first_name, candidate.last_name
            point_scaled = self.scaleCoordinates(candidate.position)
            painter.setPen(pen)
            painter.drawPoint(point_scaled)

            painter.setPen(QColor(0, 0, 0))
            point_mapped = self.transform.map(point_scaled)
            # To prevent text inversion
            painter.setWorldMatrixEnabled(False)
            point_text = self.getTextPosition(point_mapped)
            painter.drawText(point_mapped + point_text, f"{fst_name} {lst_name}")
            painter.setWorldMatrixEnabled(True)

    def drawPoints(self, painter: QPainter) -> None:
        """Draw the points corresponding to existing electors (without liquid democracy) and to existing candidates. 
        Args:
            painter (PySide6.QtGui.QPainter): An initialized painter.
        """

        self.drawElectors(painter)
        self.drawCandidates(painter)

    def drawElectorsDelegation(self, painter: QPainter) -> None:
        """Draw the points corresponding to the existing electors (with liquid democracy), i.e. with their weights. 

        Args:
           painter (PySide6.QtGui.QPainter): An initialized painter.
        """

        pen = QPen(QColor(128, 128, 128))
        pen.setWidth(4)
        painter.setPen(pen)
        for elector in self.election.electors:
            if elector.weight == 0:
                painter.drawPoint(self.scaleCoordinates(elector.position))

        for elector in self.election.electors:
            if elector.weight > 0:
                pen3 = QPen(QColor(30, 144, 255))
                pen3.setWidth(4)
                painter.setPen(pen3)

                scaled_point = self.scaleCoordinates(elector.position)
                point_mapped = self.transform.map(scaled_point)

                painter.drawPoint(scaled_point)
                # To prevent text inversion
                painter.setWorldMatrixEnabled(False)
                point_text = self.getTextPosition(point_mapped)
                painter.drawText(point_mapped + point_text, f"{elector.weight}")
                painter.setWorldMatrixEnabled(True)

        self.drawCandidates(painter)

    def scaleCoordinates(self, position: tuple[float, float]) -> QPointF:
        """Scale normalized position to the political map size.

        Args:
            position (tuple[float, float]): A position with normalized coordinates.

        Returns:
            PySide6.QtCore.QPointF: A point with scaled coordinates.
        """

        x, y = position
        return QPointF(x * self.width() / 2, y * self.height() / 2)

    def normalizeCoordinates(self, point: QPointF) -> tuple[float, float]:
        """Normalize point coordinates.

        Args:
            point (PySide6.QtCore.QPointF): A scaled point in the cartesian coordinate system. 

        Returns:
            tuple[float, float]: A position with normalized coordinates.
        """

        return point.x() / self.width() * 2, point.y() / self.height() * 2

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Redefine `mousePressEvent` by default. Left click: place the candidate manually and enter his full name.
            Right click: place the elector manually."""

        inverted_transform, _ = self.transform.inverted()
        point_inv = inverted_transform.map(event.position())
        normalized_pos = self.normalizeCoordinates(point_inv)
        # Left click
        if event.button() == Qt.LeftButton:
            self.election.add_elector(normalized_pos)
            self.update()

        # Right click
        if event.button() == Qt.RightButton and not self.text_box_active:
            # Text zone
            self.createTextBox(event.position(), normalized_pos)
            self.text_box_active = True

    def createTextBox(self, point: QPointF, normalized_pos: tuple[float, float]) -> None:
        """Create a textbox when creating the candidate manually.

        Args:
            point (PySide6.QtCore.QPointF): A point on the political map (in the computer coordinate system). 
            normalized_pos (tuple[float, float]): A position of `point` but normalized and in the cartesion coordinate system. 
        """

        # Text box creation
        self.text_box = QLineEdit(self)

        # Place the text box on the given position with an offset
        self.text_box.move(self.getTextBoxPosition(point, self.text_box.size()))

        # Call the function which will create the candidate on `Enter` press 
        self.text_box.returnPressed.connect(lambda: self.storeName(normalized_pos))

        self.text_box.show()

    def storeName(self, normalized_pos: tuple[float, float]) -> None:
        """Store the candidate's full name. First and last names are required.
        Create the candidate, add it to the election. Delete a textbox. Redraw the political map.

        Args:
            normalized_pos (tuple[float, float]): A normalized position in the cartesian coordinate system.
        """

        # Get text 
        full_name = self.text_box.text().strip().split(" ", 1)
        # Prohibit the creation of the candidate with only first name
        if len(full_name) >= 2:
            first_name, last_name = tuple(full_name)
            self.election.add_candidate(normalized_pos, first_name, last_name)
            self.update()
            
        self.text_box_active = False
        # Delete textbox
        self.text_box.deleteLater()

    def getTextPosition(self, point: QPointF) -> QPointF:
        """Calculate text coordinates within the political map limits.

        Args:
            point (PySide6.QtCore.QPointF): A point in the computer coordinate system.
                This is the origin point (from which the offset will be calculated).

        Returns:
            PySide6.QtCore.QPointF: A point with an offset. This point is in the computer coordinate system.
        """

        point_text = QPoint(5, 15)
        shift = point + point_text

        # Over the map on X & Y
        if shift.x() + 100 > self.width() and shift.y() + 100 > self.height():
            # Inverse, flip X & Y
            point_text = QPointF(-point_text.y(), -point_text.x())
        # Over the map on X
        elif shift.x() + 100 > self.width():
            point_text = QPointF(-point_text.x(), point_text.y())
        # Over the map on Y
        elif shift.y() + 100 > self.height():
            point_text = QPointF(point_text.x(), -point_text.y())

        return point_text

    def getTextBoxPosition(self, point: QPointF, size: QSize) -> QPoint:
        """Calculate textbox coordinates with the political map limits. 

        Args:
            point (PySide6.QtCore.QPointF): A point in the computer coordinate system. 
                This is to the origin point (from which the offset will be calculated).
            size (PySide6.QtCore.QSize): Textbox size.

        Returns:
            PySide6.QtCore.QPoint: A point with an offset. This point is in the computer coordinate system.
        """

        width, height = size.width(), size.height()
        point_textbox = point.toPoint()
        if point.x() + width > self.width():
            point_textbox = QPoint(point_textbox.x() - width, point_textbox.y())
        if point.y() + height > self.height():
            point_textbox = QPoint(point_textbox.x(), point_textbox.y() - height)

        return point_textbox

    def generateCoordinate(self, mu: float, sigma: float, limit: float) -> float:
        """Generate a coordinate (X or Y) according to the normal distribution (`mu`, `sigma` are its parameters).
            An absolute value of a generated coordinates is limited between `limit`. 

        Args:
            mu (float): The mean of the normal distribution. 
            sigma (float): The variance of the normal distribution. A strictly positive float.
            limit (float): Upper and lower limit of a coordinate.

        Returns:
            float: A generated and limited coordinate.
        """

        coordinate = normal(mu, sigma)

        # Max tries of a coordinate generation. Without it, an infinite loop is possible.
        max_iterations = 5
        while abs(coordinate) > limit and max_iterations:
            coordinate = normal(mu, sigma)
            max_iterations -= 1

        coordinate = clip(coordinate, -limit, limit)

        return coordinate

    def generatePosition(self) -> tuple[float, float]:
        """Generate a position on the political map according to the normal distribution.

        Returns:
            tuple[float, float]: A generated position with normalized and confined coordinates.
        """

        constants = self.election.generation_constants
        economical_constants = constants[RandomConstants.ECONOMICAL]
        social_constants = constants[RandomConstants.SOCIAL]
        coef_dir = constants[RandomConstants.ORIENTATION]

        mu, sigma = economical_constants[0], economical_constants[1]
        x = self.generateCoordinate(mu, sigma, limit=1)

        mu, sigma = coef_dir * x + social_constants[0], social_constants[1]
        y = self.generateCoordinate(mu, sigma, limit=1)
        return (x, y)
