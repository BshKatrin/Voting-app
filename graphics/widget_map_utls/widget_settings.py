from PySide6.QtWidgets import *
from PySide6.QtCore import *
from sys import argv, exit

from .quadrant_map import QuadrantMap


class WidgetSettings(QWidget):
    def __init__(self,parent,election):
        super().__init__()
        self.election=election
        self.setWindowTitle("Random generation settings")

        self.economical_label = QLabel('Economical',self)
        self.social_label = QLabel('Social', self)

        self.mu_eco_label=QLabel('mu', self)
        self.sigma_eco_label=QLabel('sigma',self)
        self.mu_social_label=QLabel('mu', self)
        self.sigma_social_label=QLabel('sigma',self)

        self.mu_eco_result=QLabel('', self)
        self.sigma_eco_result=QLabel('',self)
        self.mu_social_result=QLabel('', self)
        self.sigma_social_result=QLabel('',self)
        
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
        
        
        #mise en place du layout
        self.layout_widget = QGridLayout()
        self.setLayout(self.layout_widget)
        #implementation des titres
        self.layout_widget.addWidget(self.economical_label,1,2)
        self.layout_widget.addWidget(self.social_label,1,5)
        #implementation des slider dans le layout
        self.layout_widget.addWidget(self.slider_mu_eco,3,2)
        self.layout_widget.addWidget(self.slider_sigma_eco,4,2)
        self.layout_widget.addWidget(self.slider_mu_socio,3,5)
        self.layout_widget.addWidget(self.slider_sigma_socio,4,5)
        #implementation des labes des slider
        self.layout_widget.addWidget(self.mu_eco_label,3,1)
        self.layout_widget.addWidget(self.sigma_eco_label,4,1)
        self.layout_widget.addWidget(self.mu_social_label,3,4)
        self.layout_widget.addWidget(self.sigma_social_label,4,4)
        #implementation des valeurs des slider 
        self.layout_widget.addWidget(self.mu_eco_result,3,3)
        self.layout_widget.addWidget(self.sigma_eco_result,4,3)
        self.layout_widget.addWidget(self.mu_social_result,3,6)
        self.layout_widget.addWidget(self.sigma_social_result,4,6)


    def majMuEcoValue(self, value):
        self.election.economical_constants=(int(value*(5.6)),self.election.economical_constants[1])
        self.mu_eco_result.setText(f'Current Value: {value}')
        

    def majMuSocioValue(self, value):
        self.election.social_constants=(int(value*(5.6)),self.election.social_constants[1])
        self.mu_social_result.setText(f'Current Value: {value}')
        

    def majSigmaEcoValue(self, value):
        self.election.economical_constants=(self.election.economical_constants[0],abs(int(value*(5.6)-self.election.economical_constants[0])))
        self.sigma_eco_result.setText(f'Current Value: {value}')
        

    def majSigmaSocioValue(self, value):
        self.election.social_constants=(self.election.social_constants[0],abs(int(value*(5.6)-self.election.social_constants[0])))
        self.sigma_social_result.setText(f'Current Value: {value}')



if __name__ == "__main__":
    app = QApplication(argv)
    app.setStyle("Fusion")

    window = WidgetSettings(app)

    window.show()
    exit(app.exec())