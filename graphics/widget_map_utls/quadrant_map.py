from itertools import product
from math import sqrt

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtCore import Qt, QPointF

from numpy import clip
from numpy.random import normal
from electoral_systems import Election, RandomConstants

from people import Elector, Candidate


class QuadrantMap(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.electors = []  #   stock les coordonées cartésiennes des votants
        self.candidates = []  #   stock les coordonées cartésiennes des candidats

        self.election = Election()
        self.final_painting = False
        side_size = min(parent.width(), parent.height())
        self.setFixedSize(0.8 * side_size, 0.8 * side_size)

        self.initUI()

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

    ### fonction sans argument qui dessines les points de candidates et electors dans le graph
    def drawPoints(self, painter):
        offset = QPointF(
            self.width() / 2, self.height() / 2
        )  #   position du milieu (0,0)

        #   dessin des points des élécteurs
        pen = QPen(QColor(0, 0, 255))
        pen.setWidth(4)
        painter.setPen(pen)
        for elector in self.election.electors:
            (x, y) = elector.position
            pos = QPointF(x, y) * self.width() / 2
            #   crée un widget de position du point et lui affecte la position du point actuel
            widget_pos = QPointF(pos.x() + offset.x(), offset.y() - pos.y())
            painter.drawPoint(widget_pos)

        #   dessin des points des candidates
        pen2 = QPen(QColor(255, 0, 0))
        pen2.setWidth(4)
        painter.setPen(pen2)
        for candidate in self.election.candidates:
            fst_name, lst_name = candidate.first_name, candidate.last_name
            x, y = candidate.position
            pos = QPointF(x, y) * self.width() / 2
            painter.setPen(
                pen2
            )  #   reconfiguration du pinceau après une itération de la boucle
            widget_pos = QPointF(pos.x() + offset.x(), offset.y() - pos.y())
            painter.drawPoint(widget_pos)

            #   reconfiguration du style du pinceau pour le texte
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(widget_pos + QPointF(5, 15), f"{fst_name} {lst_name}")

    def drawPointsDelegation(self, painter):
        offset = QPointF(
            self.width() / 2, self.height() / 2
        )  #   position du milieu (0,0)

        #   dessin des points des élécteurs
        pen = QPen(QColor(128, 128, 128))
        pen.setWidth(4)
        painter.setPen(pen)
        for elec in self.election.electors:
            #   crée un widget de position du point et lui affecte la position du point actuel
            if elec.weight == 0:
                (x, y) = elec.position
                x = x * self.width() / 2
                y = y * self.height() / 2
                widget_pos = QPointF(x + offset.x(), offset.y() - y)
                painter.drawPoint(widget_pos)

        pen3 = QPen(QColor(30, 144, 255))
        pen3.setWidth(4)
        painter.setPen(pen3)
        for elec in self.election.electors:
            if elec.weight > 0:
                (x, y) = elec.position
                x = x * self.width() / 2
                y = y * self.height() / 2
                widget_pos = QPointF(x + offset.x(), offset.y() - y)
                painter.drawPoint(widget_pos)
                painter.drawText(widget_pos + QPointF(5, 15), f"{elec.weight}")

        #   dessin des points des candidates
        pen2 = QPen(QColor(255, 0, 0))
        pen2.setWidth(4)
        painter.setPen(pen2)
        for fst_name, lst_name, pos in self.candidates:
            painter.setPen(
                pen2
            )  #   reconfiguration du pinceau après une itération de la boucle
            widget_pos = QPointF(pos.x() + offset.x(), offset.y() - pos.y())
            painter.drawPoint(widget_pos)

            #   reconfiguration du style du pinceau pour le texte
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(widget_pos + QPointF(5, 15), f"{fst_name} {lst_name}")

    ### fonction sans argument qui est appelé lors d'un clique de souris et créé un candidat en clique droit ou stock les coordonnées d'un elector
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  #   cas du clique gauche
            offset = QPointF(self.width() // 2, self.height() // 2)

            #   récupère la position du point cliqué en position cartésienne
            cartesian_pos = QPointF(
                event.pos().x() - offset.x(), offset.y() - event.pos().y()
            )
            self.electors.append(cartesian_pos)
            # self.election.add_electors_position(self.normalizePosition(cartesian_pos))
            self.election.add_elector(Elector(candidates=self.election.candidates))
            self.update()  #   actualise l'état graphique du tableau (les points et leurs positions)

        # cas du clique droit
        if event.button() == Qt.RightButton and not self.text_box_active:
            # appelle de la création de la zone de texte
            self.createTextBox(event.pos())
            self.text_box_active = True

    ### fonction sans argument qui créé une textbox lors de la création manuelle d'un candidat
    def createTextBox(self, position):
        self.text_box = QLineEdit(self)  #   création de la zone de texte
        self.text_box.move(
            position
        )  #   placement de la zone de texte à la position clique
        self.text_box.returnPressed.connect(
            lambda: self.storeName(position)
        )  #   appelle de la fonction de création et de stockage du nom connecté avec la touche enter
        self.text_box.show()  #   Affiche la zone de texte la zone de texte

    ### fonction sans argument appelée par la textbox de création du candidat pour stocker le nom det créer le candidat
    def storeName(self, position):
        # récupère le texte dans une variable
        full_name = self.text_box.text().split(" ", 1)
        first_name, last_name = tuple(full_name)

        #   création du candidat et stockage dans le tableau
        offset = QPointF(self.width() // 2, self.height() // 2)

        cartesian_pos = QPointF(position.x() - offset.x(), offset.y() - position.y())
        self.candidates.append((first_name, last_name, cartesian_pos))
        self.election.add_candidate(
            Candidate(
                first_name=first_name,
                last_name=last_name,
                position=self.normalizePosition(cartesian_pos),
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

        ### generer QPointF(x, y), PAS normalise

    def generatePosition(self):

        constants = self.election.generation_constants
        economical_constants = constants[RandomConstants.ECONOMICAL]
        social_constants = constants[RandomConstants.SOCIAL]
        coef_dir = constants[RandomConstants.ORIENTATION]
        # Spread factor on a map for sigma

        mu, sigma = economical_constants[0], economical_constants[1]
        print(mu, sigma)
        x = self._generate_coordinate(mu, sigma, limit=1)

        mu, sigma = coef_dir * x + social_constants[0], social_constants[1]
        print(mu, sigma)
        y = self._generate_coordinate(mu, sigma, limit=1)

        # Limit values  to a map range
        # x = clip(x, -1, 1)
        # y = clip(y, -1, 1)

        # Scaling
        half_width = self.width() / 2
        return QPointF(x * half_width, y * half_width)

    ### Position de type QPointF, retourne couple normale
    def normalizePosition(self, position):
        return position.x() / self.width() * 2, position.y() / self.height() * 2
