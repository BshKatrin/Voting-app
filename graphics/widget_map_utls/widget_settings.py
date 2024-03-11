from PySide6.QtWidgets import *
from PySide6.QtCore import *
from sys import argv, exit


class WidgetSettings(QWidget):
    def __init__(self,parent):
        super().__init__()
        self.setWindowTitle("Random generation settings")
        self.slider_mu_eco = QSlider(Qt.Horizontal,self)
        self.slider_mu_eco.setValue(280)
        self.slider_mu_eco.setMinimum(0)
        self.slider_mu_eco.setMaximum(560)
        self.slider_sigma_eco = QSlider(Qt.Horizontal,self)
        self.slider_mu_socio = QSlider(Qt.Vertical,self)
        self.slider_sigma_socio = QSlider(Qt.Vertical,self)
        
        
        
        self.layout_widget = QGridLayout()
        self.setLayout(self.layout_widget)
        self.layout_widget.addWidget(self.slider_mu_socio,1,2)
        self.layout_widget.addWidget(self.slider_mu_eco,2,3)
        self.layout_widget.addWidget(self.slider_sigma_socio,1,1)
        self.layout_widget.addWidget(self.slider_sigma_eco,3,3)





if __name__ == "__main__":
    app = QApplication(argv)
    app.setStyle("Fusion")

    window = WidgetSettings(app)

    window.show()
    exit(app.exec())