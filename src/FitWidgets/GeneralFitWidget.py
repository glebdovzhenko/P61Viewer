from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QFileDialog
from PyQt5.QtCore import Qt, QWaitCondition, QMutex
import pandas as pd
import numpy as np
import logging
import copy

from P61App import P61App
from DatasetManager import DatasetViewer
from FitWidgets.LmfitInspector import LmfitInspector
from FitWidgets.CopyPopUp import CopyPopUp
from FitWidgets.SeqFitPopUp import SeqFitPopUp
from FitWidgets.ConstrainPopUp import ConstrainPopUp
from PlotWidgets import FitPlot
from ThreadIO import Worker
from lmfit_utils import fit_peaks, fit_bckg


class FitWorker(Worker):
    def __init__(self, x, y, res, fit_type):
        def fn_all(xx, yy, result):
            result = fit_bckg(xx, yy, result)
            result = fit_peaks(xx, yy, result)
            result = fit_bckg(xx, yy, result)
            return result

        if fit_type == 'peaks':
            super(FitWorker, self).__init__(fit_peaks, args=[], kwargs={'xx': x, 'yy': y, 'result': res})
        elif fit_type == 'bckg':
            super(FitWorker, self).__init__(fit_bckg, args=[], kwargs={'xx': x, 'yy': y, 'result': res})
        elif fit_type == 'all':
            super(FitWorker, self).__init__(fn_all, args=[], kwargs={'xx': x, 'yy': y, 'result': res})
        else:
            raise ValueError('fit_type argument should be \'peaks\' or \'bckg\'')

        self.threadWorkerException = self.q_app.fitWorkerException
        self.threadWorkerResult = self.q_app.fitWorkerResult
        self.threadWorkerFinished = self.q_app.fitWorkerFinished
        self.threadWorkerStatus = self.q_app.fitWorkerStatus


class GeneralFitWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()
        self.logger = logging.getLogger(str(self.__class__))

        self.fit_idx = None

        self.lmfit_inspector = LmfitInspector()

        self.active_list = DatasetViewer()

        self.fit_btn = QPushButton('Fit')
        self.constrain_btn = QPushButton('Constrain parameters')
        self.bckg_fit_btn = QPushButton('Fit Background')
        self.peaks_fit_btn = QPushButton('Fit peaks')
        self.fit_all_btn = QPushButton('Fit multiple')
        self.copy_btn = QPushButton('Copy params')
        self.export_btn = QPushButton('Export')
        self.plot_w = FitPlot(parent=self)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.lmfit_inspector, 1, 1, 3, 3)
        layout.addWidget(self.active_list, 4, 2, 6, 2)
        # layout.addWidget(self.fit_btn, 4, 1, 1, 1)
        layout.addWidget(self.constrain_btn, 4, 1, 1, 1)
        layout.addWidget(self.bckg_fit_btn, 5, 1, 1, 1)
        layout.addWidget(self.peaks_fit_btn, 6, 1, 1, 1)
        layout.addWidget(self.copy_btn, 7, 1, 1, 1)
        layout.addWidget(self.fit_all_btn, 8, 1, 1, 1)
        layout.addWidget(self.export_btn, 9, 1, 1, 1)
        layout.addWidget(self.plot_w, 1, 4, 8, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 6)

        # self.fit_btn.clicked.connect(self.on_fit_btn)
        self.constrain_btn.clicked.connect(self.on_constrain_btn)
        self.fit_all_btn.clicked.connect(self.on_fit_all_btn)
        self.bckg_fit_btn.clicked.connect(self.on_bckg_fit_btn)
        self.peaks_fit_btn.clicked.connect(self.on_peak_fit_btn)
        self.copy_btn.clicked.connect(self.on_copy_btn)
        self.export_btn.clicked.connect(self.on_export_button)

        self.q_app.fitWorkerResult.connect(self.on_tw_result, Qt.QueuedConnection)
        self.q_app.fitWorkerException.connect(self.on_tw_exception, Qt.QueuedConnection)
        self.q_app.fitWorkerFinished.connect(self.on_tw_finished, Qt.QueuedConnection)

    def on_tw_finished(self):
        self.logger.debug('on_tw_finished: Handling FitWorker.threadWorkerFinished')
        self.fit_idx = None

    def on_tw_result(self, result):
        self.logger.debug('on_tw_result: Handling FitWorker.threadWorkerResult')
        self.q_app.set_general_result(self.fit_idx, result)

    def on_tw_exception(self):
        self.logger.debug('on_tw_exception: Handling FitWorker.threadWorkerException')

    def on_constrain_btn(self, *args, idx=None):
        w = ConstrainPopUp(parent=self)
        w.exec_()

    def on_peak_fit_btn(self, *args, idx=None):
        if self.fit_idx is not None:
            return

        if self.q_app.get_selected_idx() == -1:
            return

        elif idx is None:
            idx = self.q_app.get_selected_idx()

        result = self.q_app.get_general_result(idx)
        if result is None:
            return

        xx, yy = self.q_app.data.loc[idx, 'DataX'], self.q_app.data.loc[idx, 'DataY']
        # x_lim = self.plot_w.get_axes_xlim()
        # yy = yy[(xx > x_lim[0]) & (xx < x_lim[1])]
        # xx = xx[(xx > x_lim[0]) & (xx < x_lim[1])]

        fw = FitWorker(xx, yy, copy.deepcopy(result), fit_type='peaks')
        self.fit_idx = idx
        if self.q_app.config['use_threads']:
            self.q_app.thread_pool.start(fw)
        else:
            fw.run()

    def on_bckg_fit_btn(self, *args, idx=None):
        if self.fit_idx is not None:
            return

        if self.q_app.get_selected_idx() == -1:
            return
        elif idx is None:
            idx = self.q_app.get_selected_idx()

        result = self.q_app.get_general_result(idx)
        if result is None:
            return

        xx, yy = self.q_app.data.loc[idx, 'DataX'], self.q_app.data.loc[idx, 'DataY']
        # x_lim = self.plot_w.get_axes_xlim()
        # yy = yy[(xx > x_lim[0]) & (xx < x_lim[1])]
        # xx = xx[(xx > x_lim[0]) & (xx < x_lim[1])]

        fw = FitWorker(copy.deepcopy(xx), copy.deepcopy(yy), copy.deepcopy(result), fit_type='bckg')
        self.fit_idx = idx
        if self.q_app.config['use_threads']:
            self.q_app.thread_pool.start(fw)
        else:
            fw.run()

    def on_fit_btn(self, *args, idx=None):
        if self.fit_idx is not None:
            return

        if self.q_app.get_selected_idx() == -1:
            return
        elif idx is None:
            idx = self.q_app.get_selected_idx()

        result = self.q_app.get_general_result(idx)
        if result is None:
            return

        xx, yy = self.q_app.data.loc[idx, 'DataX'], self.q_app.data.loc[idx, 'DataY']
        # x_lim = self.plot_w.get_axes_xlim()
        # yy = yy[(xx > x_lim[0]) & (xx < x_lim[1])]
        # xx = xx[(xx > x_lim[0]) & (xx < x_lim[1])]

        fw = FitWorker(xx, yy, copy.deepcopy(result), fit_type='all')
        self.fit_idx = idx
        if self.q_app.config['use_threads']:
            self.q_app.thread_pool.start(fw)
        else:
            fw.run()

    def on_copy_btn(self, *args):
        w = CopyPopUp(parent=self)
        w.exec_()

    def on_fit_all_btn(self):
        w = SeqFitPopUp(parent=self)
        w.exec_()

    def on_export_button(self):
        f_name, _ = QFileDialog.getSaveFileName(self, "Save fit data as csv", "", "All Files (*);;CSV (*.csv)")
        if not f_name:
            return

        def expand_result(row):
            if row['GeneralFitResult'] is None:
                return pd.Series({'ScreenName': row['ScreenName'], 'DeadTime': row['DeadTime']})
            else:
                n_row = {'ScreenName': row['ScreenName'], 'DeadTime': row['DeadTime'],
                         'chisqr': row['GeneralFitResult'].chisqr}
                for p in row['GeneralFitResult'].params:
                    n_row = {**n_row, p: row['GeneralFitResult'].params[p].value, p + '_std': row['GeneralFitResult'].params[p].stderr}
                return pd.Series(n_row)

        result = pd.DataFrame()
        result = result.append(self.q_app.data.loc[self.q_app.data['Active'], ['ScreenName', 'DeadTime',
                                                                               'GeneralFitResult']])
        result = result.apply(expand_result, axis=1)
        result.to_csv(f_name)


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = GeneralFitWidget()
    app.show()
    sys.exit(q_app.exec())