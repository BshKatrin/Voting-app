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
        
        #configuration taille du window
        side_size = min(parent.width(), parent.height())
        self.setFixedSize(0.8*side_size,0.8* side_size)

        self.scrollArea = QScrollArea()

        #Creations des graph
        self.economical_graph = GraphSettings(self.election,'Left-Right')
        self.social_graph = GraphSettings(self.election, 'Liberal-Autoritarian')
        self.coeffdir_graph = GraphSettings(self.election, 'Coefficient directeur')
        self.knowledge_graph =GraphSettings(self.election, 'Knowledge')
        
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

        
        
        #mise en place Wigdet economical
        self.layout_economical_widget = QGridLayout()
        self.layout_economical_widget.addWidget(self.economical_label,1,2)
        self.layout_economical_widget.addWidget(self.economical_graph,2,2)
        self.layout_economical_widget.addWidget(self.mu_eco_label,3,1)
        self.layout_economical_widget.addWidget(self.slider_mu_eco,3,2)
        self.layout_economical_widget.addWidget(self.mu_eco_result,3,3)
        self.layout_economical_widget.addWidget(self.sigma_eco_label,4,1)
        self.layout_economical_widget.addWidget(self.slider_sigma_eco,4,2)
        self.layout_economical_widget.addWidget(self.sigma_eco_result,4,3)
        self.widget_economical = QWidget()
        self.widget_economical.setFixedSize(400,400)
        self.widget_economical.setLayout(self.layout_economical_widget)

        #mise en place Wigdet social
        self.layout_social_widget = QGridLayout()
        self.layout_social_widget.addWidget(self.social_label,1,2)
        self.layout_social_widget.addWidget(self.social_graph,2,2)
        self.layout_social_widget.addWidget(self.mu_social_label,3,1)
        self.layout_social_widget.addWidget(self.slider_mu_socio,3,2)
        self.layout_social_widget.addWidget(self.mu_social_result,3,3)
        self.layout_social_widget.addWidget(self.sigma_social_label,4,1)
        self.layout_social_widget.addWidget(self.slider_sigma_socio,4,2)
        self.layout_social_widget.addWidget(self.sigma_social_result,4,3)
        self.widget_social = QWidget()
        self.widget_social.setFixedSize(400,400)
        self.widget_social.setLayout(self.layout_social_widget)

        #mise en place Wigdet Coeffdir
        self.layout_coeffdir_widget = QGridLayout()
        self.layout_coeffdir_widget.addWidget(self.coeffdir_label,1,2)
        self.layout_coeffdir_widget.addWidget(self.coeffdir_graph,2,2)
        self.layout_coeffdir_widget.addWidget(self.coeffdir_label,3,1)
        self.layout_coeffdir_widget.addWidget(self.slider_coeffdir,3,2)
        self.layout_coeffdir_widget.addWidget(self.coeffdir_result,3,3)
        self.widget_coeffdir = QWidget()
        self.widget_coeffdir.setFixedSize(400,400)
        self.widget_coeffdir.setLayout(self.layout_coeffdir_widget)

        #mise en place Wigdet Knowledge
        self.layout_knowledge_widget = QGridLayout()
        self.layout_knowledge_widget.addWidget(self.knowledge_label,1,2)
        self.layout_knowledge_widget.addWidget(self.knowledge_graph,2,2)
        self.layout_knowledge_widget.addWidget(self.mu_knowledge_label,3,1)
        self.layout_knowledge_widget.addWidget(self.slider_mu_knowledge,3,2)
        self.layout_knowledge_widget.addWidget(self.mu_knowledge_result,3,3)
        self.layout_knowledge_widget.addWidget(self.sigma_knowledge_label,4,1)
        self.layout_knowledge_widget.addWidget(self.slider_sigma_knowledge,4,2)
        self.layout_knowledge_widget.addWidget(self.sigma_knowledge_result,4,3)
        self.widget_knowledge = QWidget()
        self.widget_knowledge.setFixedSize(400,400)
        self.widget_knowledge.setLayout(self.layout_knowledge_widget)

        #mise en place du widget scrollable
        self.layout_scroll_widget = QVBoxLayout()
        self.layout_scroll_widget.addWidget(self.widget_economical)
        self.layout_scroll_widget.addWidget(self.widget_social )
        self.layout_scroll_widget.addWidget(self.widget_coeffdir)
        self.layout_scroll_widget.addWidget(self.widget_knowledge)
        self.widget_scroll = QWidget()
        self.widget_scroll.setLayout(self.layout_scroll_widget)
        
        #mise en place du layout de la fenetre implementant le widget scrolable 
        self.scrollArea.setWidget(self.widget_scroll)
        self.layout_principal = QVBoxLayout()
        self.layout_principal.addWidget(self.scrollArea)
        self.setLayout(self.layout_principal)


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
        self.knowledge_graph.updateGraphGauss(self.election.knowledge_constants[0],self.election.knowledge_constants[1])
        

    def majSigmaKnowledgeValue(self, value):
        self.election.knowledge_constants=(self.election.knowledge_constants[0],abs(self.election.knowledge_constants[0]-value/100))
        self.sigma_knowledge_result.setText(f'{value/100}')
        self.knowledge_graph.updateGraphGauss(self.election.knowledge_constants[0],self.election.knowledge_constants[1])

    def majCoeffdirValue(self,value):
        self.election.coef_dir = value
        self.coeffdir_result.setText(f'{self.election.coef_dir}')
        self.coeffdir_graph.updateGraphAffine(self.election.coef_dir,(self.election.social_constants[0]-280)/560)

