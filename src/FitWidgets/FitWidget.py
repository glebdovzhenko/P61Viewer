from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton
from functools import reduce

from P61App import P61App
from ListWidgets import ActiveListWidget
from FitWidgets.FitModelInspectorWidget import LmFitInspectorWidget
from FitWidgets.FitModelBuilderWidget import FitModelBuilderWidget


class FitWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.lmfit_builder = FitModelBuilderWidget()
        self.lmfit_inspector = LmFitInspectorWidget(parent=self)

        self.active_list = ActiveListWidget()

        self.fit_btn = QPushButton('Fit this')
        self.fit_all_btn = QPushButton('Fit all')
        self.export_btn = QPushButton('Export')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.lmfit_builder, 1, 1, 1, 3)
        layout.addWidget(self.lmfit_inspector, 2, 1, 1, 3)
        layout.addWidget(self.active_list, 3, 2, 3, 2)
        layout.addWidget(self.fit_btn, 3, 1, 1, 1)
        layout.addWidget(self.fit_all_btn, 4, 1, 1, 1)
        layout.addWidget(self.export_btn, 5, 1, 1, 1)

        self.fit_btn.clicked.connect(self.on_fit_btn)
        self.fit_all_btn.clicked.connect(self.on_fit_all_btn)

    def on_fit_btn(self, *args, idx=None):
        if self.q_app.params['SelectedIndex'] == -1:
            return
        elif idx is None:
            idx = self.q_app.params['SelectedIndex']

        model = self.q_app.params['LmFitModel']
        xx, yy = self.q_app.data.loc[idx, 'DataX'], self.q_app.data.loc[idx, 'DataY']
        sel = (self.q_app.params['PlotXLim'][0] < xx) & (self.q_app.params['PlotXLim'][1] > xx)
        xx, yy = xx[sel], yy[sel]

        if self.q_app.data.loc[idx, 'FitResult'] is None:
            params = reduce(lambda a, b: a + b, (cmp.guess(yy, x=xx) for cmp in model.components))
        else:
            params = self.q_app.data.loc[idx, 'FitResult'].params

        self.q_app.data.loc[idx, 'FitResult'] = model.fit(yy, x=xx, params=params)
        self.lmfit_inspector.update_repr()
        # TODO: this is a temporary hack. should be another signal.
        self.q_app.selectedIndexChanged.emit(self.q_app.params['SelectedIndex'])

    def on_fit_all_btn(self):
        idxs = self.q_app.data[self.q_app.data['Active']].index
        for idx in idxs:
            self.on_fit_btn(idx=idx)


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = FitWidget()
    app.show()
    sys.exit(q_app.exec())