from PySide6.QtWidgets import *
from PySide6.QtCore import *
from sys import argv, exit

from .quadrant_map import QuadrantMap


class WidgetSettings(QWidget):
    def __init__(self,parent,election):
        super().__init__()
        self.election=election
        self.setWindowTitle("Random generation settings")

        self.map=QuadrantMap(parent=self)

        self.mu_label=QLabel('mu', self)
        self.sigma_label=QLabel('sigma',self)
        self.mu_social_label=QLabel('mu', self)
        self.sigma_social_label=QLabel('sigma',self)
        
        self.slider_mu_eco = QSlider(Qt.Horizontal,self)
        self.slider_mu_eco.valueChanged.connect(self.majMuEcoValue)
        self.slider_mu_eco.setValue(int(self.election.economical_constants[0]/5.6))
        self.slider_mu_eco.setRange(0,100)

        self.slider_mu_socio = QSlider(Qt.Vertical,self)
        self.slider_mu_socio.valueChanged.connect(self.majMuSocioValue)
        self.slider_mu_socio.setValue(int(self.election.social_constants[0]/5.6))
        self.slider_mu_socio.setRange(0,100)
        
        self.slider_sigma_eco = QSlider(Qt.Horizontal,self)
        self.slider_sigma_eco.valueChanged.connect(self.majSigmaEcoValue)
        self.slider_sigma_eco.setValue(int(self.election.economical_constants[1]/5.6+self.election.economical_constants[0]/5.6))
        self.slider_sigma_eco.setRange(0,100)
        
        
        self.slider_sigma_socio = QSlider(Qt.Vertical,self)
        self.slider_sigma_socio.valueChanged.connect(self.majSigmaSocioValue)
        self.slider_sigma_socio.setValue(int(self.election.social_constants[1]/5.6+self.election.social_constants[0]/5.6))
        self.slider_sigma_socio.setRange(0,100)
        
        
        
        self.layout_widget = QGridLayout()
        self.setLayout(self.layout_widget)
        self.layout_widget.addWidget(self.slider_mu_socio,1,2)
        self.layout_widget.addWidget(self.slider_mu_eco,3,4)
        self.layout_widget.addWidget(self.slider_sigma_socio,1,1)
        self.layout_widget.addWidget(self.slider_sigma_eco,4,4)
        self.layout_widget.addWidget(self.map,1,4)
        self.layout_widget.addWidget(self.mu_social_label,2,2)
        self.layout_widget.addWidget(self.mu_label,3,3)
        self.layout_widget.addWidget(self.sigma_social_label,2,1)
        self.layout_widget.addWidget(self.sigma_label,4,3)

    def majMuEcoValue(self, value):
        self.election.economical_constants=(int(value*(5.6)),self.election.economical_constants[1])
        

    def majMuSocioValue(self, value):
        self.election.social_constants=(int(value*(5.6)),self.election.social_constants[1])
        

    def majSigmaEcoValue(self, value):
        self.election.economical_constants=(self.election.economical_constants[0],abs(int(value*(5.6)-self.election.economical_constants[0])))
        

    def majSigmaSocioValue(self, value):
        self.election.social_constants=(self.election.social_constants[0],abs(int(value*(5.6)-self.election.social_constants[0])))



if __name__ == "__main__":
    app = QApplication(argv)
    app.setStyle("Fusion")

    window = WidgetSettings(app)

    window.show()
    exit(app.exec())