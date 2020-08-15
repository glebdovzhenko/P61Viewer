from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QErrorMessage, QFileDialog
import pandas as pd

from P61App import P61App
from DatasetManager import DatasetViewer
from FitWidgets.LmfitInspector import LmfitInspector
from FitWidgets.CopyPopUp import CopyPopUp
from FitWidgets.SeqFitPopUp import SeqFitPopUp
from PlotWidgets import FitPlot


class GeneralFitWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.lmfit_inspector = LmfitInspector()

        self.active_list = DatasetViewer()

        self.fit_btn = QPushButton('Fit this')
        self.fit_all_btn = QPushButton('Fit multiple')
        self.copy_btn = QPushButton('Copy params')
        self.export_btn = QPushButton('Export')
        self.plot_w = FitPlot(parent=self)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.lmfit_inspector, 1, 1, 3, 3)
        layout.addWidget(self.active_list, 4, 2, 4, 2)
        layout.addWidget(self.fit_btn, 4, 1, 1, 1)
        layout.addWidget(self.copy_btn, 5, 1, 1, 1)
        layout.addWidget(self.fit_all_btn, 6, 1, 1, 1)
        layout.addWidget(self.export_btn, 7, 1, 1, 1)
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
        w = CopyPopUp(parent=self)
        w.exec_()

    def on_fit_btn(self, *args, idx=None):
        if self.q_app.get_selected_idx() == -1:
            return
        elif idx is None:
            idx = self.q_app.get_selected_idx()

        result = self.q_app.get_general_result(idx)
        if result is None:
            return

        xx, yy = self.q_app.data.loc[idx, 'DataX'], self.q_app.data.loc[idx, 'DataY']
        x_lim = self.plot_w.get_axes_xlim()
        sel = (x_lim[0] < xx) & (x_lim[1] > xx)
        xx, yy = xx[sel], yy[sel]

        vary_params = dict()
        for model in result.model.components:
            if ('GaussianModel' in model.name) or \
                    ('LorentzianModel' in model.name) or \
                    ('PseudoVoigtModel' in model.name):
                if not x_lim[0] <= result.params[model.prefix + 'center'].value <= x_lim[1]:
                    for param in result.params:
                        if model.prefix in param:
                            vary_params[param] = result.params[param].vary
                            result.params[param].vary = False

        try:
            result.fit(yy, x=xx, workers=8, max_nfev=1000, method='least_squares')
        except Exception as e:
            msg = QErrorMessage()
            msg.showMessage('During fit of %s an exception occured:\n' % self.q_app.data.loc[idx, 'ScreenName'] + str(e))
            msg.exec_()

        for param in vary_params:
            result.params[param].vary = vary_params[param]

        self.q_app.set_general_result(idx, result)

    def on_fit_all_btn(self):
        w = SeqFitPopUp(parent=self)
        w.exec_()

    def on_export_button(self):
        f_name, _ = QFileDialog.getSaveFileName(self, "Save fit data as csv", "", "All Files (*);;CSV (*.csv)")
        if not f_name:
            return

        def expand_result(row):
            if row['GeneralFitResult'] is None:
                return pd.Series({'ScreenName': row['ScreenName']})
            else:
                n_row = {'ScreenName': row['ScreenName'], 'chisqr': row['GeneralFitResult'].chisqr}
                for p in row['GeneralFitResult'].params:
                    n_row = {**n_row, p: row['GeneralFitResult'].params[p].value, p + '_std': row['GeneralFitResult'].params[p].stderr}
                return pd.Series(n_row)

        result = pd.DataFrame()
        result = result.append(self.q_app.data.loc[self.q_app.data['Active'], ['ScreenName', 'GeneralFitResult']])
        result = result.apply(expand_result, axis=1)
        result.to_csv(f_name)


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = GeneralFitWidget()
    app.show()
    sys.exit(q_app.exec())