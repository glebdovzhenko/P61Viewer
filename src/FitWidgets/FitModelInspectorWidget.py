from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
import numpy as np
from functools import reduce

from P61BApp import P61BApp
from FitWidgets.FitParamWidget import FitParamWidget


class FitModelInspector(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61BApp.instance()

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

        if (model is None) and (fit_results is None):
            self.setFixedHeight(20)
            self.setFixedWidth(100)
            return

        if fit_results is None:
            self.init_fit()
            fit_results = self.q_app.data.loc[self.q_app.params['SelectedIndex'], 'FitResult']

        for k in fit_results.params:
            self.param_widgets[k] = FitParamWidget(parent=self, name=k, value=fit_results.params[k].value,
                                                   error=np.inf, label_w=110)
            self.layout.addWidget(self.param_widgets[k])

        self.setFixedHeight(1.4 * sum(map(lambda x: x.height(), self.param_widgets.values())))
        self.setFixedWidth(1.1 * max(map(lambda x: x.width(), self.param_widgets.values())))

    def init_fit(self):
        if self.q_app.params['SelectedIndex'] == -1:
            return
        else:
            idx = self.q_app.params['SelectedIndex']

        model = self.q_app.params['LmFitModel']
        xx, yy = self.q_app.data.loc[idx, 'DataX'], self.q_app.data.loc[idx, 'DataY']
        sel = (self.q_app.params['PlotXLim'][0] < xx) & (self.q_app.params['PlotXLim'][1] > xx)
        xx, yy = xx[sel], yy[sel]

        params = reduce(lambda a, b: a + b, (cmp.guess(yy, x=xx) for cmp in model.components))
        result = model.fit(yy, x=xx, params=params)
        self.q_app.data.loc[idx, 'FitResult'] = result
        # print(result.fit_report())


class LmFitInspectorWidget(QScrollArea):
    def __init__(self, parent=None):
        QScrollArea.__init__(self, parent=parent)
        self.inspector = FitModelInspector()
        self.setWidget(self.inspector)


if __name__ == '__main__':
    import sys

    q_app = P61BApp(sys.argv)
    fw = LmFitInspectorWidget()
    fw.show()
    sys.exit(q_app.exec())