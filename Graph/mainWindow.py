from PySide6.QtCore import QSize
from PySide6.QtGui import QAction,QIcon
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
import sys
from grapheManual import GraphManualWindow
from grapheRandom import GraphRandomWindow
from votingSystem import VoteSystemWindow

class HomeWindow(QMainWindow):
    def __init__(self,app):
        super().__init__()
        self.app = app
        #dimension et titre de la fenetre (posX,posY,tailleX,tailleY)
        self.setGeometry(0, 0, 1000, 500)
        self.setWindowTitle("Fenêtre Principale")

        #Menu bar 
        menu_bar=self.menuBar()
        #Menu FILE 
        file_menu= menu_bar.addMenu("file")
        quit_action= file_menu.addAction("quit")
        quit_action.triggered.connect(self.quit_app)
        
        #Bouton permettant d'acceder au differentes fenêtres
        button_qraphic= QPushButton("Manual graph")
        button_qraphic.setFixedSize(150,30)
        button_qraphic.clicked.connect(self.graphManualButtonClicked)
        button_randGraph= QPushButton("Random Graph")
        button_randGraph.setFixedSize(150,30)
        button_randGraph.clicked.connect(self.graphRandomButtonClicked)


        #Layout du Central Widget 
        layout=QVBoxLayout()
        layout.addWidget(button_qraphic)
        layout.addWidget(button_randGraph)

        #Creation du widget central et affectation du layout
        centralWidget=QWidget(self)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)


    def graphManualButtonClicked(self,app):
        graphWindow=GraphManualWindow(app)
        self.close()
        graphWindow.show()
        sys.exit(app.exec())

    def graphRandomButtonClicked(self,app):
        graphWindow=GraphRandomWindow(app)
        self.close()
        graphWindow.show()
        sys.exit(app.exec())

    def buttonClicked(self):
        print("button clicked")

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