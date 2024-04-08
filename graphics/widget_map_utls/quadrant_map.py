from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QTransform, QColor
from PySide6.QtCore import Qt, QPointF, QPoint

from numpy import clip
from numpy.random import normal
from electoral_systems import Election, RandomConstants


class QuadrantMap(QWidget):
    def __init__(self, size_proportion, parent):
        super().__init__(parent)

        self.election = Election()
        self.draw_delegations = False

        side_size = min(parent.width(), parent.height())
        self.setFixedSize(size_proportion * side_size, size_proportion * side_size)

        self.setTransformation()
        self.initUI()

    def setTransformation(self):
        self.transform = QTransform()
        # Order matters!
        # Flip Y-axis
        self.transform.scale(1, -1)
        # Move center
        self.transform.translate(self.width() / 2, -self.height() / 2)

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.setPallete()

        self.grid_step = 20
        self.text_box_active = False

    # Set background color : white
    def setPallete(self):
        self.setAutoFillBackground(True)
        pallete = self.palette()
        pallete.setColor(self.backgroundRole(), QColor(255, 255, 255))
        self.setPalette(pallete)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawGrid(painter)
        self.drawAxes(painter)
        self.drawAxisLabels(painter)

        painter.setTransform(self.transform)

        if self.draw_delegations:
            self.drawElectorsDelegation(painter)
        else:
            self.drawPoints(painter)

    # Draw grid
    def drawGrid(self, painter):
        # Couleur de la grille gris clair
        pen = QPen(QColor(220, 220, 220))
        painter.setPen(pen)
        # nb_lines = nb_rows = nb_cols
        nb_lines = self.width() // self.grid_step

        for row in range(1, nb_lines + 1):
            # lignes verticales
            painter.drawLine(
                row * self.grid_step, 0, row * self.grid_step, self.height()
            )
            # lignes horizontales
            painter.drawLine(
                0, row * self.grid_step, self.width(), row * self.grid_step
            )

    # Draw axes X, Y
    def drawAxes(self, painter):
        # Black color
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)

        # Width = height, donc suffisant
        central_line = self.width() // self.grid_step / 2
        painter.setPen(pen)
        # Axe x
        painter.drawLine(
            0,
            central_line * self.grid_step,
            self.width(),
            central_line * self.grid_step,
        )
        # Axe y
        painter.drawLine(
            central_line * self.grid_step,
            0,
            central_line * self.grid_step,
            self.height(),
        )

    # Draw text labels on endpoints
    def drawAxisLabels(self, painter):
        # Black color
        pen = QPen(QColor(0, 0, 0))
        painter.setPen(pen)
        # QFont permet de définir les propriétés de la police
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        # applique les propriétés du QFont au pinceau
        painter.setFont(font)

        painter.drawText(self.width() - 40, self.height() / 2 + 30, "Right")
        painter.drawText(self.width() / 2 - 85, 20, "Autoritarian")
        painter.drawText(self.width() / 150, self.height() / 2 + 30, "Left")
        painter.drawText(self.width() / 2 - 60, self.height() - 10, "Liberal")

    # Dessin des points des élécteurs (sans poids)
    def drawElectors(self, painter):
        # Standard blut color
        pen = QPen(QColor(0, 0, 255))
        pen.setWidth(4)
        painter.setPen(pen)
        for elector in self.election.electors:
            painter.drawPoint(self.scaleCoordinates(elector.position))

    # Dessin des points candidats
    def drawCandidates(self, painter):
        # Standard red color
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(4)
        painter.setPen(pen)
        for candidate in self.election.candidates:
            fst_name, lst_name = candidate.first_name, candidate.last_name
            #   reconfiguration du pinceau après une itération de la boucle
            point_scaled = self.scaleCoordinates(candidate.position)
            painter.setPen(pen)
            painter.drawPoint(point_scaled)

            #   reconfiguration du style du pinceau pour le texte
            painter.setPen(QColor(0, 0, 0))
            point_mapped = self.transform.map(point_scaled)
            # To prevent text inverse
            painter.setWorldMatrixEnabled(False)
            point_text = self.getTextPosition(point_mapped)
            painter.drawText(point_mapped + point_text, f"{fst_name} {lst_name}")
            painter.setWorldMatrixEnabled(True)

    ### fonction sans argument qui dessines les points de candidates et electors dans le graph
    def drawPoints(self, painter):
        #   dessin des points des élécteurs
        self.drawElectors(painter)
        self.drawCandidates(painter)

    def drawElectorsDelegation(self, painter):
        #   dessin des points des élécteurs
        pen = QPen(QColor(128, 128, 128))
        pen.setWidth(4)
        painter.setPen(pen)
        for elector in self.election.electors:
            #   crée un widget de position du point et lui affecte la position du point actuel
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
                # To prevent text inverse
                painter.setWorldMatrixEnabled(False)
                point_text = self.getTextPosition(point_mapped)
                painter.drawText(point_mapped + point_text, f"{elector.weight}")
                painter.setWorldMatrixEnabled(True)

        self.drawCandidates(painter)

    def scaleCoordinates(self, position):
        x, y = position
        return QPointF(x * self.width() / 2, y * self.height() / 2)

    def normalizeCoordinates(self, point):
        return point.x() / self.width() * 2, point.y() / self.height() * 2

    ### fonction sans argument qui est appelé lors d'un clique de souris et créé un candidat en clique droit ou stock les coordonnées d'un elector
    def mousePressEvent(self, event):
        inverted_transform, _ = self.transform.inverted()
        point_inv = inverted_transform.map(event.position())
        normalized_pos = self.normalizeCoordinates(point_inv)
        if event.button() == Qt.LeftButton:  #   cas du clique gauche
            self.election.add_elector(normalized_pos)
            self.update()

        # cas du clique droit
        if event.button() == Qt.RightButton and not self.text_box_active:
            # appelle de la création de la zone de texte
            self.createTextBox(event.position(), normalized_pos)
            self.text_box_active = True

    ### fonction sans argument qui créé une textbox lors de la création manuelle d'un candidat
    def createTextBox(self, point, normalized_pos):
        self.text_box = QLineEdit(self)  #   création de la zone de texte

        #   placement de la zone de texte à la position clique
        self.text_box.move(self.getTextBoxPosition(point, self.text_box.size()))
        #   appelle de la fonction de création et de stockage du nom connecté avec la touche enter
        self.text_box.returnPressed.connect(lambda: self.storeName(normalized_pos))
        self.text_box.show()  #   Affiche la zone de texte la zone de texte

    ### fonction sans argument appelée par la textbox de création du candidat pour stocker le nom det créer le candidat
    def storeName(self, normalized_pos):
        # récupère le texte dans une variable
        full_name = self.text_box.text().split(" ", 1)
        # Prohibit the creation of candidates with only first name
        if len(full_name) == 1:
            return
        first_name, last_name = tuple(full_name)

        self.election.add_candidate(normalized_pos, first_name, last_name)
        self.update()
        self.text_box_active = False
        self.text_box.deleteLater()  #   supprime la zone de texte

    # point : QPoitntF of a point to which text is associated
    # Function returns QPointF where text should be drawn so it is visible
    # point IS mapped (meaning it is computer coordinate)
    def getTextPosition(self, point):
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

    def getTextBoxPosition(self, point, size):
        width, height = size.width(), size.height()
        point_textbox = point.toPoint()
        if point.x() + width > self.width():
            point_textbox = QPoint(point_textbox.x() - width, point_textbox.y())
        if point.y() + height > self.height():
            point_textbox = QPoint(point_textbox.x(), point_textbox.y() - height)

        return point_textbox

        # Generate x or y based on an already scaled mu & sigma

    def generateCoordinate(self, mu, sigma, limit):
        # Generate while not in border
        coordinate = normal(mu, sigma)
        max_iterations = 5
        while abs(coordinate) > limit and max_iterations:
            coordinate = normal(mu, sigma)
            max_iterations -= 1

        # If value is still out of border, otherwise eternal loop
        coordinate = clip(coordinate, -1, 1)
        return coordinate

    # Generate (x, y) normalized
    def generatePosition(self):

        constants = self.election.generation_constants
        economical_constants = constants[RandomConstants.ECONOMICAL]
        social_constants = constants[RandomConstants.SOCIAL]
        coef_dir = constants[RandomConstants.ORIENTATION]
        # Spread factor on a map for sigma

        mu, sigma = economical_constants[0], economical_constants[1]
        x = self.generateCoordinate(mu, sigma, limit=1)

        mu, sigma = coef_dir * x + social_constants[0], social_constants[1]
        y = self.generateCoordinate(mu, sigma, limit=1)

        return (x, y)
