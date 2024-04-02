from itertools import product
from math import sqrt
from functools import partial

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QSizePolicy
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QTransform
from PySide6.QtCore import Qt, QPointF, QPoint

from numpy import clip
from numpy.random import normal
from electoral_systems import Election, RandomConstants

from people import Elector, Candidate


class QuadrantMap(QWidget):
    def __init__(self, size_proportion, parent):
        super().__init__(parent)

        self.election = Election()
        self.final_painting = False

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
        # Set background color : white
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        # Pour gérer les textbox de création de candidats
        self.grid_step = 20  # pas de création de la grille
        self.text_box_active = False

    ### fonction sans argument crée tout ce qui doit être sessiné et est mit à jour lors d'un appel à update
    # appelle les fonctions de création graphique du graph
    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawGrid(painter)
        self.drawAxes(painter)
        self.drawAxisLabels(painter)

        painter.setTransform(self.transform)

        if self.final_painting:
            self.drawPointsDelegation(painter)
        else:
            self.drawPoints(painter)

    ### fonction sans argument de création de la grille du graph de dimensions fixées dans la fonction
    def drawGrid(self, painter):
        pen = QPen(QColor(220, 220, 220))  #   couleur de la grille gris clair
        # tout les dessins appelant QPainter donc tout ce qui est déssiné ensuite utilisera le pinceau défini
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

        # for x in range(0, self.width(), step):  #   lignes verticales
        #     painter.drawLine(x, 0, x, self.height())  #   appelle de fonction de dessin
        # for y in range(0, self.height(), step):  #   lignes horozontales
        #     painter.drawLine(0, y, self.width(), y)

    ### fonction sans argument de création des axes du graph
    def drawAxes(self, painter):
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)  #   taille du pinceau
        step = 20
        # Width = height, donc suffisant
        central_line = self.width() // step / 2
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

    ### fonction sans argument qui donne des noms aux graphs
    def drawAxisLabels(self, painter):
        pen = QPen(QColor(0, 0, 0))
        painter.setPen(pen)
        font = QFont()  #   QFont permet de définir les propriétés de la police
        font.setFamily("Arial")
        font.setPointSize(10)
        painter.setFont(font)  #  applique les propriétés du QFont au pinceau

        painter.drawText(self.width() - 40, self.height() / 2 + 30, "Right")
        painter.drawText(self.width() / 2 - 85, 20, "Autoritarian")
        painter.drawText(self.width() / 150, self.height() / 2 + 30, "Left")
        painter.drawText(self.width() / 2 - 60, self.height() - 10, "Liberal")

    def _drawElectors(self, painter):

        #   dessin des points des élécteurs
        pen = QPen(QColor(0, 0, 255))
        pen.setWidth(4)
        painter.setPen(pen)
        for elector in self.election.electors:
            painter.drawPoint(self.scaleCoordinates(elector.position))

    def _drawCandidates(self, painter):
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
            point_text = self.getTextPosition(point_mapped, shift_point=QPointF(5, 15))
            painter.drawText(point_mapped + point_text, f"{fst_name} {lst_name}")
            painter.setWorldMatrixEnabled(True)

    ### fonction sans argument qui dessines les points de candidates et electors dans le graph
    def drawPoints(self, painter):
        #   dessin des points des élécteurs
        self._drawElectors(painter)
        self._drawCandidates(painter)

    def drawPointsDelegation(self, painter):
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
                point_text = self.getTextPosition(
                    point_mapped, shift_point=QPointF(5, 15)
                )
                painter.drawText(point_mapped + point_text, f"{elector.weight}")
                painter.setWorldMatrixEnabled(True)

        self._drawCandidates(painter)

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
            knowledge_const = self.election.generation_constants[
                RandomConstants.KNOWLEDGE
            ]
            self.election.add_elector(
                Elector(position=normalized_pos, knowledge_const=knowledge_const)
            )

            # self.electors_map_data.append(point_inv)
            self.update()  #   actualise l'état graphique du tableau (les points et leurs positions)

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

        if len(full_name) == 1:
            first_name = full_name[0]
            last_name = " "
            if not first_name:
                self.text_box_active = False
                self.text_box.deleteLater()  #   supprime la zone de texte
                return
        else:
            first_name, last_name = tuple(full_name)

        # self.candidates_map_data.append((first_name, last_name, point_inv))
        dogma_const = self.election.generation_constants[RandomConstants.DOGMATISM]
        oppos_const = self.election.generation_constants[RandomConstants.OPPOSITION]
        self.election.add_candidate(
            Candidate(
                first_name=first_name,
                last_name=last_name,
                position=normalized_pos,
                dogmatism_const=dogma_const,
                opposition_const=oppos_const,
            )
        )
        self.update()
        self.text_box_active = False
        self.text_box.deleteLater()  #   supprime la zone de texte

    # Generate x or y based on an already scaled mu & sigma
    def _generate_coordinate(self, mu, sigma, limit):
        # Generate while not in border
        coordinate = normal(mu, sigma)
        while abs(coordinate) > limit:
            coordinate = normal(mu, sigma)
        return coordinate

    # Generate (x, y) normalized
    def generatePosition(self):

        constants = self.election.generation_constants
        economical_constants = constants[RandomConstants.ECONOMICAL]
        social_constants = constants[RandomConstants.SOCIAL]
        coef_dir = constants[RandomConstants.ORIENTATION]
        # Spread factor on a map for sigma

        mu, sigma = economical_constants[0], economical_constants[1]
        x = self._generate_coordinate(mu, sigma, limit=1)

        mu, sigma = coef_dir * x + social_constants[0], social_constants[1]
        y = self._generate_coordinate(mu, sigma, limit=1)

        # Limit values  to a map range
        # x = clip(x, -1, 1)
        # y = clip(y, -1, 1)

        return (x, y)

    # point : QPoitntF of a point to which text is associated
    # Function returns QPointF where text should be drawn so it is visible
    # point IS mapped (meaning it is computer coordinate)
    def getTextPosition(self, point, shift_point):
        point_text = shift_point
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
