from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QApplication,
)
import sys

from .graph_manual import GraphManualWindow
from .settings import *
from .graph import Graph

# from graph_random import GraphRandomWindow
# from votingSystem import VoteSystemWindow


class HomeWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        # dimension et titre de la fenetre (posX,posY,tailleX,tailleY)
        self.setGeometry(0, 0, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.setWindowTitle("Voting app")

        # Menu bar
        self.menu_bar = self.menuBar()
        # Menu FILE
        self.file_menu = self.menu_bar.addMenu("file")
        self.quit_action = self.file_menu.addAction("quit")
        self.quit_action.triggered.connect(self.quit_app)
        self.menu_bar.setNativeMenuBar(
            False
        )  # pour fixer le bug : menu_bar n'est pas visible

        # Bouton permettant d'acceder au differentes fenêtres
        self.button_qraphic = QPushButton("Manual graph")
        self.button_qraphic.setFixedSize(150, 30)
        self.button_qraphic.clicked.connect(self.graphManualButtonClicked)
        self.button_randGraph = QPushButton("Random Graph")
        self.button_randGraph.setFixedSize(150, 30)
        # button_randGraph.clicked.connect(self.graphRandomButtonClicked)

        # Layout du Central Widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.button_qraphic)
        self.layout.addWidget(self.button_randGraph)

        # Creation du widget central et affectation du layout
        self.centralWidget = QWidget(self)
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)

    def graphManualButtonClicked(self):
        # clear window
        self.clearWindow()
        # place new widget

        self.manualGraph = Graph()
        self.layout.addWidget(self.manualGraph)
        # for i in range(self.layout.count()):
        #     print(self.layout.itemAt(i).widget())

    def clearWindow(self):
        for i in reversed(range(self.layout.count())):
            widgetToRemove = self.layout.itemAt(i).widget()
            # Supprimer widget dans layout_list
            self.layout.removeWidget(widgetToRemove)
            # Supprimer widget dans main_winddow
            widgetToRemove.setParent(None)

    #     graphWindow = GraphManualWindow(app)
    #     self.close()
    #     graphWindow.show()
    #     # sys.exit(app.exec())

    # def graphRandomButtonClicked(self, app):
    #     graphWindow = GraphRandomWindow(app)
    #     self.close()
    #     graphWindow.show()

    #  sys.exit(app.exec())

    def quit_app(self):
        self.app.quit()


""""
class GraphRandomWindow(QMainWindow):
    def __init__(self,app):
        super().__init__()
        self.app=app
        #Dimension et titre de la fenêtre 
        self.setGeometry(0,0,1000,500)
        self.setWindowTitle("Random graphic Window")

        #creation des bouton
        button_result=QPushButton("Voting results")
        button_result.setFixedSize(150,30)
        button_result.clicked.connect(self.resultButtonClicked)
        button_home=QPushButton("Home")
        button_home.setFixedSize(100,25)
        button_home.clicked.connect(self.homeButtonClicked)

        #def du layout
        layout=QVBoxLayout()
        layout.addWidget(button_result)

        #Creation du widget central et affectation du layout
        centralWidget=QWidget(self)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        #Creation du status bar et mise du bouton
        status_bar=self.statusBar()
        status_bar.addWidget(button_home)


    def resultButtonClicked(self,app):
        voteWindow=VoteSystemWindow(app)
        self.close()
        voteWindow.show()
        sys.exit(app.exec())

    def homeButtonClicked(self,app):
        homeWindow=HomeWindow(app)
        self.close()
        homeWindow.show()
        sys.exit(app.exec())
"""

if __name__ == "__main__":
    app = QApplication()
    window = HomeWindow(sys.argv)
    window.show()
    sys.exit(app.exec())
