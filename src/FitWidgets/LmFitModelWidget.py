from PyQt5.QtWidgets import QWidget, QVBoxLayout
import numpy as np
from lmfit import Model
from lmfit.models import PseudoVoigtModel, LinearModel

from P61BApp import P61BApp
from FitWidgets.FitParamWidget import FitParamWidget


class LmfitModelWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self.param_widgets = dict()
        P61BApp.instance().project.compositeModelUpdated.connect(self.on_composite_model_upd)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.on_composite_model_upd()

    def on_composite_model_upd(self):
        for k in self.param_widgets:
            self.layout.removeWidget(self.param_widgets[k])
            self.param_widgets[k].setParent(None)
        self.param_widgets.clear()

        model = P61BApp.instance().project.lmfit_composite_model
        for ii, k in enumerate(model.param_names):
            self.param_widgets[k] = FitParamWidget(parent=self, name=k, value=0.0, error=np.inf, label_w=100)
            self.layout.addWidget(self.param_widgets[k])



if __name__ == '__main__':
    import sys

    q_app = P61BApp(sys.argv)
    fw = LmfitModelWidget()
    fw.show()
    sys.exit(q_app.exec())