from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtCore import Qt, QPoint
import random, string

from electoral_systems import Election
from electoral_systems.voting_rules import constants

from people import Elector
from people import Candidate

from ..settings import MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT


class QuadrantMap(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.electors = []  #   stock les coordonées cartésiennes des votants
        self.candidates = []  #   stock les coordonées cartésiennes des candidats

        self.election = Election()

        self.setFixedSize(0.7 * MAIN_WINDOW_WIDTH, 0.7 * MAIN_WINDOW_HEIGHT)

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        # Set background color : white
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        # Pour gérer les textbox de création de candidats
        self.text_box_active = False

    ### fonction sans argument crée tout ce qui doit être sessiné et est mit à jour lors d'un appel à update
    # appelle les fonctions de création graphique du graph
    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawGrid(painter)
        self.drawAxes(painter)
        self.drawAxisLabels(painter)
        self.drawPoints(painter)

    ### fonction sans argument de création de la grille du graph de dimensions fixées dans la fonction
    def drawGrid(self, painter):
        pen = QPen(QColor(220, 220, 220))  #   couleur de la grille gris clair
        # tout les dessins appelant QPainter donc tout ce qui est déssiné ensuite utilisera le pinceau défini
        painter.setPen(pen)
        step = 20  #   pas de création de la grille

        for x in range(0, self.width(), step):  #   lignes verticales
            painter.drawLine(x, 0, x, self.height())  #   appelle de fonction de dessin
        for y in range(0, self.height(), step):  #   lignes horozontales
            painter.drawLine(0, y, self.width(), y)

    ### fonction sans argument de création des axes du graph
    def drawAxes(self, painter):
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)  #   taille du pinceau
        painter.setPen(pen)
        center_x = self.width() / 2
        center_y = self.height() / 2
        painter.drawLine(0, center_y, self.width(), center_y)
        painter.drawLine(center_x, 0, center_x, self.height())

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
        offset = QPoint(
            self.width() / 2, self.height() / 2
        )  #   position du milieu (0,0)

        #   dessin des points des élécteurs
        pen = QPen(QColor(0, 0, 255))
        pen.setWidth(4)
        painter.setPen(pen)
        for pos in self.electors:
            #   crée un widget de position du point et lui affecte la position du point actuel
            widget_pos = QPoint(pos.x() + offset.x(), offset.y() - pos.y())
            painter.drawPoint(widget_pos)

        #   dessin des points des candidates
        pen2 = QPen(QColor(255, 0, 0))
        pen2.setWidth(4)
        painter.setPen(pen2)
        for fst_name, lst_name, pos in self.candidates:
            painter.setPen(
                pen2
            )  #   reconfiguration du pinceau après une itération de la boucle
            widget_pos = QPoint(pos.x() + offset.x(), offset.y() - pos.y())
            painter.drawPoint(widget_pos)

            #   reconfiguration du style du pinceau pour le texte
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(widget_pos + QPoint(5, 15), f"{fst_name} {lst_name}")

    ### fonction sans argument qui est appelé lors d'un clique de souris et créé un candidat en clique droit ou stock les coordonnées d'un elector
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  #   cas du clique gauche
            offset = QPoint(self.width() // 2, self.height() // 2)

            #   récupère la position du point cliqué en position cartésienne
            cartesian_pos = QPoint(
                event.pos().x() - offset.x(), offset.y() - event.pos().y()
            )
            self.electors.append(cartesian_pos)
            self.election.add_electors_position(self.normalizePosition(cartesian_pos))
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
        offset = QPoint(self.width() // 2, self.height() // 2)

        cartesian_pos = QPoint(position.x() - offset.x(), offset.y() - position.y())
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

    ### generer QPoint(x, y), PAS normalise
    def generatePosition(self):
        x = random.randint(-self.width() // 2, self.width() // 2)
        y = random.randint(-self.height() // 2, self.height() // 2)
        return QPoint(x, y)

    ### Position de type QPoint, retourne couple normale
    def normalizePosition(self, position):
        return position.x() / self.width() * 2, position.y() / self.height() * 2
