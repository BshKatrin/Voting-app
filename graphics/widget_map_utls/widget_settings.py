from PySide6.QtWidgets import *
from PySide6.QtCore import *
from sys import argv, exit
from .graph_settings import GraphSettings
from .quadrant_map import QuadrantMap


class WidgetSettings(QWidget):
    def __init__(self,parent,election):
        super().__init__()
        self.election=election
        self.setWindowTitle("Random generation settings")

        #Creations des graph
        self.economical_graph = GraphSettings(self.election,'Left-Right')
        self.social_graph = GraphSettings(self.election, 'Liberal-Autoritarian')
        self.coeffdir_graph = GraphSettings(self.election, 'Coefficient directeur')
        
        """self.economical_graph.updateGraphGauss(self.election.economical_constants[0]/560,self.election.economical_constants[1]/560)
        self.social_graph.updateGraphGauss(self.election.social_constants[0]/560,self.election.social_constants[1]/560)
        self.coeffdir_graph.updateGraphAffine(self.election.coef_dir,(self.election.social_constants[0]-280)/560)"""

        

        self.economical_label = QLabel('Economical',self)
        self.social_label = QLabel('Social', self)

        self.mu_eco_label = QLabel('Mu', self)
        self.sigma_eco_label = QLabel('Sigma',self)
        self.mu_social_label = QLabel('Mu', self)
        self.sigma_social_label = QLabel('Sigma',self)
        self.coeffdir_label = QLabel('Coeffdir',self)

        self.mu_eco_result = QLabel('', self)
        self.sigma_eco_result = QLabel('',self)
        self.mu_social_result = QLabel('', self)
        self.sigma_social_result = QLabel('',self)
        self.coeffdir_result = QLabel('',self)
        
        self.slider_mu_eco = QSlider(Qt.Horizontal,self)
        self.slider_mu_eco.valueChanged.connect(self.majMuEcoValue)
        self.slider_mu_eco.setValue(int(self.election.economical_constants[0]/5.6))
        self.slider_mu_eco.setRange(0,100)

        self.slider_mu_socio = QSlider(Qt.Horizontal,self)
        self.slider_mu_socio.valueChanged.connect(self.majMuSocioValue)
        self.slider_mu_socio.setValue(int(self.election.social_constants[0]/5.6))
        self.slider_mu_socio.setRange(0,100)
        
        self.slider_sigma_eco = QSlider(Qt.Horizontal,self)
        self.slider_sigma_eco.valueChanged.connect(self.majSigmaEcoValue)
        self.slider_sigma_eco.setValue(int(self.election.economical_constants[1]/5.6+self.election.economical_constants[0]/5.6))
        self.slider_sigma_eco.setRange(0,100)
        
        
        self.slider_sigma_socio = QSlider(Qt.Horizontal,self)
        self.slider_sigma_socio.valueChanged.connect(self.majSigmaSocioValue)
        self.slider_sigma_socio.setValue(int(self.election.social_constants[1]/5.6+self.election.social_constants[0]/5.6))
        self.slider_sigma_socio.setRange(0,100)
        
        self.slider_coeffdir = QSlider(Qt.Horizontal, self)
        self.slider_coeffdir.valueChanged.connect(self.majCoeffdirValue)
        self.slider_coeffdir.setValue(self.election.coef_dir)
        self.slider_coeffdir.setRange(-1,1)
        self.slider_coeffdir.setTickInterval(1)

        
        #Labels ajoutés pour calculer les niveau de compétences des électeurs de manière aléatoire suivant une loi normale
        self.knowledge_label = QLabel('Knowledge', self)
        
        self.mu_knowledge_label=QLabel('mu', self)
        self.sigma_knowledge_label=QLabel('sigma',self)
        
        self.mu_knowledge_result=QLabel('', self)
        self.sigma_knowledge_result=QLabel('',self)

        self.slider_mu_knowledge = QSlider(Qt.Horizontal,self)
        self.slider_mu_knowledge.valueChanged.connect(self.majMuKnowledgeValue)
        self.slider_mu_knowledge.setValue(self.election.knowledge_constants[0]*100)
        self.slider_mu_knowledge.setRange(0,100)
        
        self.slider_sigma_knowledge = QSlider(Qt.Horizontal,self)
        self.slider_sigma_knowledge.valueChanged.connect(self.majSigmaKnowledgeValue)
        self.slider_sigma_knowledge.setValue(self.election.knowledge_constants[1]*100)
        self.slider_sigma_knowledge.setRange(0,100)

        
        
        #mise en place du layout
        self.layout_widget = QGridLayout()
        self.setLayout(self.layout_widget)
        #implementation des titres
        self.layout_widget.addWidget(self.economical_label,1,2)
        self.layout_widget.addWidget(self.social_label,1,5)
        self.layout_widget.addWidget(self.knowledge_label,5,2)
        #implementation des slider dans le layout
        self.layout_widget.addWidget(self.slider_mu_eco,3,2)
        self.layout_widget.addWidget(self.slider_sigma_eco,4,2)
        self.layout_widget.addWidget(self.slider_mu_socio,3,5)
        self.layout_widget.addWidget(self.slider_sigma_socio,4,5)
        self.layout_widget.addWidget(self.slider_mu_knowledge,6,2)
        self.layout_widget.addWidget(self.slider_sigma_knowledge,7,2)
        self.layout_widget.addWidget(self.slider_coeffdir,6,5)
        #implementation des labes des slider
        self.layout_widget.addWidget(self.mu_eco_label,3,1)
        self.layout_widget.addWidget(self.sigma_eco_label,4,1)
        self.layout_widget.addWidget(self.mu_social_label,3,4)
        self.layout_widget.addWidget(self.sigma_social_label,4,4)
        self.layout_widget.addWidget(self.mu_knowledge_label,6,1)
        self.layout_widget.addWidget(self.sigma_knowledge_label,7,1)
        self.layout_widget.addWidget(self.coeffdir_label,6,4)
        #implementation des valeurs des slider 
        self.layout_widget.addWidget(self.mu_eco_result,3,3)
        self.layout_widget.addWidget(self.sigma_eco_result,4,3)
        self.layout_widget.addWidget(self.mu_social_result,3,6)
        self.layout_widget.addWidget(self.sigma_social_result,4,6)
        self.layout_widget.addWidget(self.mu_knowledge_result,6,3)
        self.layout_widget.addWidget(self.sigma_knowledge_result,7,3)
        self.layout_widget.addWidget(self.coeffdir_result,6,6)
        #implementation des graphs
        self.layout_widget.addWidget(self.economical_graph,2,2)
        self.layout_widget.addWidget(self.social_graph,2,5)
        self.layout_widget.addWidget(self.coeffdir_graph,5,5)

        


    def majMuEcoValue(self, value):
        self.election.economical_constants=(int(value*(5.6)),self.election.economical_constants[1])
        self.mu_eco_result.setText(f'{value}')
        self.economical_graph.updateGraphGauss(self.election.economical_constants[0]/560,self.election.economical_constants[1]/560)

    def majMuSocioValue(self, value):
        self.election.social_constants=(int(value*(5.6)),self.election.social_constants[1])
        self.mu_social_result.setText(f'{value}')
        self.social_graph.updateGraphGauss(self.election.social_constants[0]/560,self.election.social_constants[1]/560)
        self.coeffdir_graph.updateGraphAffine(self.election.coef_dir,(self.election.social_constants[0]-280)/560)
        

    def majSigmaEcoValue(self, value):
        self.election.economical_constants=(self.election.economical_constants[0],abs(int(value*(5.6)-self.election.economical_constants[0])))
        self.sigma_eco_result.setText(f'{self.election.economical_constants[1]}')
        self.economical_graph.updateGraphGauss(self.election.economical_constants[0]/560,self.election.economical_constants[1]/560)

        

    def majSigmaSocioValue(self, value):
        self.election.social_constants=(self.election.social_constants[0],abs(int(value*(5.6)-self.election.social_constants[0])))
        self.sigma_social_result.setText(f'{self.election.social_constants[1]}')
        self.social_graph.updateGraphGauss(self.election.social_constants[0]/560,self.election.social_constants[1]/560)

    def majMuKnowledgeValue(self, value):
        self.election.knowledge_constants=(value/100,self.election.knowledge_constants[1])
        self.mu_knowledge_result.setText(f'{value/100}')
        
        

    def majSigmaKnowledgeValue(self, value):
        self.election.knowledge_constants=(self.election.knowledge_constants[0],value/100)
        self.sigma_knowledge_result.setText(f'{value/100}')


    def majCoeffdirValue(self,value):
        self.election.coef_dir = value
        self.coeffdir_result.setText(f'{self.election.coef_dir}')
        self.coeffdir_graph.updateGraphAffine(self.election.coef_dir,(self.election.social_constants[0]-280)/560)

