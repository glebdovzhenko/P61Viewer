from PyQt5.QtWidgets import QWidget, QVBoxLayout
import numpy as np

from P61BApp import P61BApp
from FitWidgets.FitParamWidget import FitParamWidget


class LmfitModelWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self.param_widgets = dict()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.update_repr(None)

    def update_repr(self, model):
        for k in self.param_widgets:
            self.layout.removeWidget(self.param_widgets[k])
            self.param_widgets[k].setParent(None)
        self.param_widgets.clear()

        if model is None:
            self.setFixedHeight(20)
            self.setFixedWidth(100)
            return

        for ii, k in enumerate(model.param_names):
            self.param_widgets[k] = FitParamWidget(parent=self, name=k, value=0.0, error=np.inf, label_w=110)
            self.layout.addWidget(self.param_widgets[k])

        self.setFixedHeight(1.4 * sum(map(lambda x: x.height(), self.param_widgets.values())))
        self.setFixedWidth(1.1 * max(map(lambda x: x.width(), self.param_widgets.values())))


if __name__ == '__main__':
    import sys

    q_app = P61BApp(sys.argv)
    fw = LmfitModelWidget()
    fw.show()
    sys.exit(q_app.exec())