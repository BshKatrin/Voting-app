from PySide6.QtWidgets import QApplication, QWidget, QMainWindow,QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from votingSystem import VoteSystemWindow
from graphe import Graph
import sys

class GraphManualWindow(QMainWindow):
    def __init__(self,app):
        super().__init__()
        self.app=app
        #Dimension et titre de la fenêtre 
        self.setGeometry(0,0,1000,1000)
        self.setWindowTitle("Graphic Window")

        #creation des bouton
        button_result=QPushButton("Voting results")
        button_result.setFixedSize(150,30)
        button_result.clicked.connect(self.resultButtonClicked)
        button_home=QPushButton("Home")
        button_home.setFixedSize(100,25)
        button_home.clicked.connect(self.homeButtonClicked)

        #creation du widget du graphe
        graph=Graph()

        #def du layout en grille (ligne,colone)
        layout=QGridLayout()
        layout.addWidget(graph,0,0)
        layout.addWidget(button_result,1,0)

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
        from mainWindow import HomeWindow
        homeWindow=HomeWindow(app)
        self.close()
        homeWindow.show()
        sys.exit(app.exec())

