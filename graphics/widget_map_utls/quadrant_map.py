from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QTransform, QColor, QPaintEvent, QMouseEvent
from PySide6.QtCore import Qt, QPointF, QPoint, QSize

from numpy import clip
from numpy.random import normal
from electoral_systems import Election, RandomConstants

# Uniquement pour une génération des docs
__pdoc__ = {
    'normal':False
}

class QuadrantMap(QWidget):
    """Un widget qui représente la carte politique. La carte politique sera dessinée à l'aide de `PySide6.QtGui.QPainter`."""

    def __init__(self, size_proportion: float, parent: QWidget):
        """Initialise une instance d'élection (pour le partage des données).

        Args:
            size_proportion (float): Une proportion de la taille d'un widget parent.
                La taille d'un widget est fixé en fonction de cette proportion.
            parent (PySide6.QtWidgets.QWidget): Un parent d'un widget.
        """

        super().__init__(parent)

        self.election = Election()
        self.draw_delegations = False

        side_size = min(parent.width(), parent.height())
        self.setFixedSize(size_proportion * side_size, size_proportion * side_size)

        self.setTransformation()
        self.initUI()

    def setTransformation(self) -> None:
        """Initialise (mais n'applique pas) la transformation des coordonnées de l'ordinateur.
        But: avoir un système des coordonnées comme en maths."""

        self.transform = QTransform()
        # L'ordre a l'importance!
        # Flip Y-axis
        self.transform.scale(1, -1)
        # Move center
        self.transform.translate(self.width() / 2, -self.height() / 2)

    def initUI(self):
        """Initialise le layout. Change la couleur d'arrière-plan sur blanc. Initialise le step pour dessiner la grille."""

        self.layout = QVBoxLayout(self)
        self.setPallete()

        self.grid_step = 20
        self.text_box_active = False

    def setPallete(self) -> None:
        """Change la couleur d'arrière-plan sur blanc."""

        self.setAutoFillBackground(True)
        pallete = self.palette()
        pallete.setColor(self.backgroundRole(), QColor(255, 255, 255))
        self.setPalette(pallete)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Redéfinit `paintEvent` par défaut. Dessine la grille, les axes X, Y. Applique la transformation.
        Dessine les points correspondants aux positions des candidats et des électeurs."""

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
        """Dessine la grille.

        Args:
            painter (PySide6.QtGui.QPainter): Un painter déjà initialisé.
        """

        # Couleur gris clair
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

    def drawAxes(self, painter: QPainter) -> None:
        """Dessine les axes X, Y.

        Args:
            painter (PySide6.QtGui.QPainter): Un painter déjà initialisé.
        """

        # Couleur noire
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

    def drawAxisLabels(self, painter: QPainter) -> None:
        """Dessine les labels des axes.

        Args:
            painter (PySide6.QtGui.QPainter): Un painter déjà initialisé.
        """

        # Couleur noire
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

    def drawElectors(self, painter: QPainter) -> None:
        """Dessine les points correspondants aux positions des électeurs (sans la démocratie liquide).

        Args:
            painter (PySide6.QtGui.QPainter): Un painter déjà initialisé.
        """

        # Couleur bleue standard
        pen = QPen(QColor(0, 0, 255))
        pen.setWidth(4)
        painter.setPen(pen)
        for elector in self.election.electors:
            painter.drawPoint(self.scaleCoordinates(elector.position))

    def drawCandidates(self, painter: QPainter) -> None:
        """Dessine les points correspondants aux positions des candidats.

        Args:
            painter (PySide6.QtGui.QPainter): Un painter déjà initialisé.
        """

        # Couleur rouge standard
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(4)
        painter.setPen(pen)
        for candidate in self.election.candidates:
            fst_name, lst_name = candidate.first_name, candidate.last_name
            # Reconfiguration du pinceau après une itération de la boucle
            point_scaled = self.scaleCoordinates(candidate.position)
            painter.setPen(pen)
            painter.drawPoint(point_scaled)

            # Reconfiguration du style du pinceau pour le texte
            painter.setPen(QColor(0, 0, 0))
            point_mapped = self.transform.map(point_scaled)
            # Pour empêcher l'inversion du texte
            painter.setWorldMatrixEnabled(False)
            point_text = self.getTextPosition(point_mapped)
            painter.drawText(point_mapped + point_text, f"{fst_name} {lst_name}")
            painter.setWorldMatrixEnabled(True)

    def drawPoints(self, painter: QPainter) -> None:
        """Dessine les points correspondants aux positions des électeurs (sans la démocratie liquide)
        et aux positions des candidats.

        Args:
            painter (PySide6.QtGui.QPainter): Un painter déjà initialisé.
        """

        self.drawElectors(painter)
        self.drawCandidates(painter)

    def drawElectorsDelegation(self, painter: QPainter) -> None:
        """Dessine les points correspondants aux positions des électeurs (avec la démocratie liquide)
        i.e. avec les poids.

        Args:
           painter (PySide6.QtGui.QPainter): Un painter déjà initialisé.
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
                # Pour empêcher l'inversion du texte
                painter.setWorldMatrixEnabled(False)
                point_text = self.getTextPosition(point_mapped)
                painter.drawText(point_mapped + point_text, f"{elector.weight}")
                painter.setWorldMatrixEnabled(True)

        self.drawCandidates(painter)

    def scaleCoordinates(self, position: tuple[float, float]) -> QPointF:
        """Met les coordonnées normalisées à l'échelle de la carte politique.

        Args:
            position (tuple[float, float]): Une position dont chaque coordonnée est normalisée.

        Returns:
            PySide6.QtCore.QPointF: Un point mis à l'échelle.
        """

        x, y = position
        return QPointF(x * self.width() / 2, y * self.height() / 2)

    def normalizeCoordinates(self, point: QPointF) -> tuple[float, float]:
        """Normalise chaque coordonnée du point.

        Args:
            point (PySide6.QtCore.QPointF): Un point mis à l'échelle dans le système de coordonnées mathématiques.

        Returns:
            tuple[float, float]: Une position dont chaque coordonnée est normalisée.
        """

        return point.x() / self.width() * 2, point.y() / self.height() * 2

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Redéfinit `mousePressEvent` par défaut. Clique gauche: place un candidat manuellement en entrant son nom et prénom.
        Clique droite: place un électeur manuellement."""

        inverted_transform, _ = self.transform.inverted()
        point_inv = inverted_transform.map(event.position())
        normalized_pos = self.normalizeCoordinates(point_inv)
        # Clique gauche
        if event.button() == Qt.LeftButton:
            self.election.add_elector(normalized_pos)
            self.update()

        # Clique droite
        if event.button() == Qt.RightButton and not self.text_box_active:
            # Création de la zone de texte
            self.createTextBox(event.position(), normalized_pos)
            self.text_box_active = True

    def createTextBox(self, point: QPointF, normalized_pos: tuple[float, float]) -> None:
        """Crée un textbox lors de la création manuelle d'un candidat.

        Args:
            point (PySide6.QtCore.QPointF): Un point sur la carte politique (dans le système des coordonnées de l'ordinateur).
            normalized_pos (tuple[float, float]): Une position du `point` mais normalisée et dans le système de coordonnées
                mathématiques.
        """

        # Création de la zone de texte
        self.text_box = QLineEdit(self)

        # Placement de la zone de texte à la position clique (avec décalage)
        self.text_box.move(self.getTextBoxPosition(point, self.text_box.size()))

        # Appelle de la fonction de création et de stockage du nom connecté avec la touche enter
        self.text_box.returnPressed.connect(lambda: self.storeName(normalized_pos))

        # Affiche la zone de texte la zone de texte
        self.text_box.show()

    def storeName(self, normalized_pos: tuple[float, float]) -> None:
        """Stocke le prénom et le nom d'un candidat créé manuellement. Le nom et le prénom sont obligatoires.
        Crée un candidat, l'ajoute dans l'élection. Supprime le textbox. Redessine la carte politique. 

        Args:
            normalized_pos (tuple[float, float]): Une position normalisée et dans le système de coordonnées mathématiques.
        """

        # Récupérer le texte
        full_name = self.text_box.text().strip().split(" ", 1)
        # Interdire la création de candidats avec uniquement le prénom
        if len(full_name) >= 2:
            first_name, last_name = tuple(full_name)
            self.election.add_candidate(normalized_pos, first_name, last_name)
            self.update()
            
        self.text_box_active = False
        # Supprime la zone de texte
        self.text_box.deleteLater()

    def getTextPosition(self, point: QPointF) -> QPointF:
        """Calcule les coordonnées du texte pour qu'il ne sort pas en dehors de la carte politique.

        Args:
            point (PySide6.QtCore.QPointF): Un point dans le système des coordonnés de l'ordinateur. Correspond au point d'origine.

        Returns:
            PySide6.QtCore.QPointF: Un point qui correpond aux coordonnées du texte où il faudra le dessiner (i.e. c'est un point
                déjà décalé à partir du `point`). C'est le point dans le système de coordonnées de l'ordinateur.
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
        """Calcule les coordonnées du textbox pour qu'il ne sorte pas en dehors de la carte politique.

        Args:
            point (PySide6.QtCore.QPointF): Un point dans le système de coordonnées de l'ordinateur. Correpond au point d'origine.
            size (PySide6.QtCore.QSize): La taille du textbox.

        Returns:
            PySide6.QtCore.QPoint: Un point qui correpond aux coordonnées du texte où il faudra le dessiner (i.e. c'est un point
                déjà décalé à partir du `point`). C'est le point dans le système de coordonnées de l'ordinateur.
        """

        width, height = size.width(), size.height()
        point_textbox = point.toPoint()
        if point.x() + width > self.width():
            point_textbox = QPoint(point_textbox.x() - width, point_textbox.y())
        if point.y() + height > self.height():
            point_textbox = QPoint(point_textbox.x(), point_textbox.y() - height)

        return point_textbox

    def generateCoordinate(self, mu: float, sigma: float, limit: float) -> float:
        """Génére une coordonnée (x ou y) selon la loi normale avec des paramètres `mu` et `sigma`.
        Borne la valeur absolue d'une coordonnée générée à limite `limit`.

        Args:
            mu (float): La moyenne de la distribution normale. 
            sigma (float): L'écart type de la distribution normale. Un réel strictement positif.
            limit (float): La limite inférieure et supérieure pour la coordonnée. 

        Returns:
            float: Une coordonnée générée et bornée.
        """

        coordinate = normal(mu, sigma)

        # Nombre max de regénération d'un coordonnée. Sinon, la boucle très longue possible
        max_iterations = 5
        while abs(coordinate) > limit and max_iterations:
            coordinate = normal(mu, sigma)
            max_iterations -= 1

        # Si la valeur regénérée est encore hors bornes
        coordinate = clip(coordinate, -1, 1)

        return coordinate

    def generatePosition(self) -> tuple[float, float]:
        """Génére une position sur la carte politique selon la loi normale.

        Returns:
            tuple[float, float]: Une position générée dont chaque coordonnée est normalisée et bornée.  
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
