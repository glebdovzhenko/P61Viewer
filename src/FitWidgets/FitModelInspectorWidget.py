from PyQt5.QtWidgets import QWidget, QVBoxLayout
import numpy as np

from P61App import P61App
from FitWidgets.FitParamWidget import FitParamWidget


class FitModelInspector(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.param_widgets = dict()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.update_repr()
        self.q_app.lmFitModelUpdated.connect(self.update_repr)
        self.q_app.selectedIndexChanged.connect(self.update_repr)

    def update_repr(self):
        for k in self.param_widgets:
            self.layout.removeWidget(self.param_widgets[k])
            self.param_widgets[k].setParent(None)
        self.param_widgets.clear()

        model = self.q_app.params['LmFitModel']
        if self.q_app.params['SelectedIndex'] == -1:
            fit_results = None
        else:
            fit_results = self.q_app.data.loc[self.q_app.params['SelectedIndex'], 'FitResult']

        if (model is None) or (fit_results is None) or (self.q_app.params['SelectedIndex'] == -1):
            self.setFixedHeight(20)
            self.setFixedWidth(100)
            return

        for k in fit_results.params:
            self.param_widgets[k] = FitParamWidget(parent=self, name=k, value=fit_results.params[k].value,
                                                   error=np.inf, label_w=110)
            self.layout.addWidget(self.param_widgets[k])

        self.setFixedHeight(1.4 * sum(map(lambda x: x.height(), self.param_widgets.values())))
        self.setFixedWidth(1.1 * max(map(lambda x: x.width(), self.param_widgets.values())))


if __name__ == '__main__':
    import sys

    q_app = P61App(sys.argv)
    fw = FitModelInspector()
    fw.show()
    sys.exit(q_app.exec())