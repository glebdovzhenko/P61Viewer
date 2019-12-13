from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QErrorMessage, QFileDialog
from functools import reduce
import pandas as pd

from P61App import P61App
from ListWidgets import ActiveListWidget
from FitWidgets.LmfitInspectorWidget import LmfitInspectorWidget
from FitWidgets.LmfitBuilderWidget import LmfitBuilderWidget
from FitWidgets.PopUpCopyWidget import PopUpCopyWidget
from FitWidgets.PopUpSeqFitWidget import PopUpSeqFitWidget
from PlotWidgets import FitPlotWidget


class FitWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.lmfit_builder = LmfitBuilderWidget()
        self.lmfit_inspector = LmfitInspectorWidget()

        self.active_list = ActiveListWidget()

        self.fit_btn = QPushButton('Fit this')
        self.fit_all_btn = QPushButton('Fit multiple')
        self.copy_btn = QPushButton('Copy params')
        self.export_btn = QPushButton('Export')
        self.plot_w = FitPlotWidget(parent=self)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.lmfit_builder, 1, 1, 1, 3)
        layout.addWidget(self.lmfit_inspector, 2, 1, 1, 3)
        layout.addWidget(self.active_list, 3, 2, 4, 2)
        layout.addWidget(self.fit_btn, 3, 1, 1, 1)
        layout.addWidget(self.copy_btn, 4, 1, 1, 1)
        layout.addWidget(self.fit_all_btn, 5, 1, 1, 1)
        layout.addWidget(self.export_btn, 6, 1, 1, 1)
        layout.addWidget(self.plot_w, 1, 4, 6, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 6)

        self.fit_btn.clicked.connect(self.on_fit_btn)
        self.fit_all_btn.clicked.connect(self.on_fit_all_btn)
        self.copy_btn.clicked.connect(self.on_copy_btn)
        self.export_btn.clicked.connect(self.on_export_button)

    def on_copy_btn(self, *args):
        w = PopUpCopyWidget(parent=self)
        w.exec_()

    def on_fit_btn(self, *args, idx=None):
        if self.q_app.params['SelectedIndex'] == -1:
            return
        elif idx is None:
            idx = self.q_app.params['SelectedIndex']

        model = self.q_app.params['LmFitModel']
        xx, yy = self.q_app.data.loc[idx, 'DataX'], self.q_app.data.loc[idx, 'DataY']
        x_lim = self.plot_w.get_axes_xlim()
        sel = (x_lim[0] < xx) & (x_lim[1] > xx)
        xx, yy = xx[sel], yy[sel]

        if self.q_app.data.loc[idx, 'FitResult'] is None:
            params = reduce(lambda a, b: a + b, (cmp.guess(yy, x=xx) for cmp in model.components))
        else:
            params = self.q_app.data.loc[idx, 'FitResult'].params
        try:
            self.q_app.data.loc[idx, 'FitResult'] = model.fit(yy, x=xx, params=params)
        except Exception as e:
            msg = QErrorMessage()
            msg.showMessage('During fit of %s an exception occured:\n' % self.q_app.data.loc[idx, 'ScreenName'] + str(e))
            msg.exec_()
        print(self.q_app.data.loc[idx, 'FitResult'].fit_report())
        self.q_app.dataFitChanged.emit([idx])

    def on_fit_all_btn(self):
        w = PopUpSeqFitWidget(parent=self)
        w.exec_()

    def on_export_button(self):
        f_name, _ = QFileDialog.getSaveFileName(self, "Save fit data as csv", "", "All Files (*);;CSV (*.csv)")
        if not f_name:
            return

        if self.q_app.params['LmFitModel'] is None:
            result = pd.DataFrame()
        else:
            result = pd.DataFrame(self.q_app.data.loc[self.q_app.data['Active'], ['ScreenName', 'FitResult']])
            for name in self.q_app.params['LmFitModel'].param_names:
                result[name] = result.apply(lambda x: x['FitResult'].params[name].value, axis=1)
                result[name + '_err'] = result.apply(lambda x: x['FitResult'].params[name].stderr, axis=1)
            result.drop('FitResult', axis=1, inplace=True)

        result.to_csv(f_name)


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = FitWidget()
    app.show()
    sys.exit(q_app.exec())