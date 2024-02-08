from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtCore import Qt, QPoint
import random, string

from electoral_systems import Election
from electoral_systems.voting_rules import constants

from people import Elector
from people import Candidate

from .settings import MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT


class Graph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.electors = []  #   stock les coordonées cartésiennes des votants
        self.electors_positions = []  #   stock les coordonnées de -1 à 1 des votants
        self.candidates = []  #   stock les coordonées cartésiennes des candidats
        self.candidates_positions = []  # stock les coordonnées de -1 à 1 des candidats

        self.election = Election()

        # dessiner grid qu'une seule fois
        if self.parent:
            self.setFixedSize(0.7 * MAIN_WINDOW_WIDTH, 0.7 * MAIN_WINDOW_HEIGHT)

        self.initUI()

    def initUI(self):

        self.layout = QVBoxLayout(self)  # layout verticale

        self.setAutoFillBackground(True)
        # Set background color : white
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    def paintEvent(self, event):  # appelle les fonctions de création graphique du graph
        painter = QPainter(self)
        self.drawGrid(painter)
        self.drawAxes(painter)
        self.drawAxisLabels(painter)
        self.drawPoints(painter)

    def drawGrid(self, painter):
        pen = QPen(QColor(220, 220, 220))  #   couleur de la grille gris clair
        # tout les dessins appelant QPainter donc tout ce qui est déssiné ensuite utilisera le pinceau défini
        painter.setPen(pen)
        step = 20  #   pas de création de la grille

        for x in range(0, self.width(), step):  #   lignes verticales
            painter.drawLine(x, 0, x, self.height())  #   appelle de fonction de dessin
        for y in range(0, self.height(), step):  #   lignes horozontales
            painter.drawLine(0, y, self.width(), y)

    def drawAxes(self, painter):
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)  #   taille du pinceau
        painter.setPen(pen)
        center_x = self.width() / 2
        center_y = self.height() / 2
        painter.drawLine(0, center_y, self.width(), center_y)
        painter.drawLine(center_x, 0, center_x, self.height())

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
        for name, pos in self.candidates:
            painter.setPen(
                pen2
            )  #   reconfiguration du pinceau après une itération de la boucle
            widget_pos = QPoint(pos.x() + offset.x(), offset.y() - pos.y())
            painter.drawPoint(widget_pos)

            #   reconfiguration du style du pinceau pour le texte
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(widget_pos + QPoint(5, 15), name)

    def mousePressEvent(self, event):
        # print("click")
        if event.button() == Qt.LeftButton:  #   cas du clique gauche
            offset = QPoint(self.width() // 2, self.height() // 2)

            #   récupère la position du point cliqué en position cartésienne
            cartesian_pos = QPoint(
                event.pos().x() - offset.x(), offset.y() - event.pos().y()
            )
            self.electors.append(cartesian_pos)
            self.election.add_elector(Elector(candidates=self.election.candidates))
            #   ajoute la position x,y du curseur dans le tableau en modifiant les valeurs pour obtenir des valeurs entre -1 et 1
            # self.electors_positions.append(
            #     (
            #         (cartesian_pos.x() / (self.width() // 2)),
            #         (cartesian_pos.y() / (self.height() // 2)),
            #     )
            # )
            self.update()  #   actualise l'état graphique du tableau (les points et leurs positions)

        if event.button() == Qt.RightButton:  #   cas du clique droit
            self.createTextBox(
                event.pos()
            )  #   appelle de la création de la zone de texte

    def createTextBox(self, position):
        self.text_box = QLineEdit(self)  #   création de la zone de texte
        self.text_box.move(
            position
        )  #   placement de la zone de texte à la position clique
        self.text_box.returnPressed.connect(
            lambda: self.storeName(position)
        )  #   appelle de la fonction de création et de stockage du nom connecté avec la touche enter
        self.text_box.show()  #   Affiche la zone de texte la zone de texte

    def storeName(self, position):
        name = self.text_box.text()  #   récupère le texte dans une variable
        print(
            f"Texte stocké : {name}"
        )  #   affiche le texte stocké pour les tests (à enlever)

        #   création du candidat et stockage dans le tableau
        offset = QPoint(self.width() // 2, self.height() // 2)

        cartesian_pos = QPoint(position.x() - offset.x(), offset.y() - position.y())

        self.candidates.append((name, cartesian_pos))
        self.election.add_candidate(
            Candidate(
                first_name=name,
                last_name=name,
                position=self.normalizePosition(cartesian_pos),
            )
        )

        self.update()
        self.text_box.deleteLater()  #   supprime la zone de texte

    # generer QPoint(x, y), PAS normalise
    def generatePosition(self):
        x = random.randint(-self.width() // 2, self.width() // 2)
        y = random.randint(-self.height() // 2, self.height() // 2)
        return QPoint(x, y)

    # Position de type QPoint, retourne couple normale
    def normalizePosition(self, position):
        print(position.x() / self.width() * 2, position.y() / self.height() * 2)
        return position.x() / self.width() * 2, position.y() / self.height() * 2

    #####   fonctions de test (à enlever)
    def showPositions(self):
        #   affiches les positions politiques des electeurs et les noms et positions des candidats dans la console
        positions_text = "\n".join(
            [f"Position: {pos[0]}, {pos[1]}" for pos in self.electors_positions]
        )
        print(positions_text)

        positions_text2 = "\n".join(
            [f"Position: {pos[0]}, {pos[1]}" for pos in self.candidates_positions]
        )
        print(positions_text2)


### appelle du widget pour des tests, je ne sais pas comment ça marchera dans un mainWindow
if __name__ == "__main__":
    app = QApplication([])
    g = Graph()
    app.exec()
