from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QDialog, QAbstractItemView, QProgressDialog
from PyQt5.Qt import Qt
from scipy.signal import find_peaks_cwt
import numpy as np

from P61App import P61App
from FitWidgets.FloatEdit import FloatEdit
from DatasetManager import DatasetSelector


class AutoFindPopUp(QDialog):
    """"""

    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.btn_ok = QPushButton('Search', parent=self)
        self.selection_list = DatasetSelector(parent=self)

        self.setWindowTitle('Auto search for peaks')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.btn_ok, 2, 1, 1, 1)
        layout.addWidget(self.selection_list, 1, 1, 1, 1)

        self.btn_ok.clicked.connect(self.on_btn_ok)

    def on_btn_ok(self):
        fit_ids = [k for k in self.selection_list.proxy.selected if self.selection_list.proxy.selected[k]]
        progress = QProgressDialog("Searching", "Cancel", 0, len(fit_ids))
        progress.setWindowModality(Qt.WindowModal)

        for ii in fit_ids:
            self.parent().on_btn_this(idx=ii)
            progress.setValue(ii)

        progress.setValue(len(fit_ids))

        self.close()


class AutoFindCWTWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.title_label = QLabel('CWT Peak Search')

        self.min_width_label = QLabel('Minimum Width')
        self.min_width_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=1.)
        self.max_width_label = QLabel('Maximum Width')
        self.max_width_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=3.)
        self.btn_this = QPushButton('Find')
        self.btn_all = QPushButton('Find in all')

        self.btn_this.clicked.connect(self.on_btn_this)
        self.btn_all.clicked.connect(self.on_btn_all)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.title_label, 1, 1, 1, 2)
        layout.addWidget(self.min_width_label, 2, 1, 1, 1)
        layout.addWidget(self.min_width_edit, 2, 2, 1, 1)
        layout.addWidget(self.max_width_label, 3, 1, 1, 1)
        layout.addWidget(self.max_width_edit, 3, 2, 1, 1)
        layout.addWidget(self.btn_this, 4, 1, 1, 1)
        layout.addWidget(self.btn_all, 4, 2, 1, 1)

    def on_btn_this(self, *args, idx=-1):
        params = {
            'widths': np.linspace(self.min_width_edit.get_value(), self.max_width_edit.get_value(), 50)
        }

        if idx == -1:
            idx = self.q_app.get_selected_idx()

        if idx != -1:
            yy = self.q_app.data.loc[idx, 'DataY']
            xx = self.q_app.data.loc[idx, 'DataX']

            if self.q_app.peak_search_range is not None:
                yy = yy[(xx < self.q_app.peak_search_range[1]) & (xx > self.q_app.peak_search_range[0])]
                xx = xx[(xx < self.q_app.peak_search_range[1]) & (xx > self.q_app.peak_search_range[0])]

            # if params['distance'] is not None:
            #     params['distance'] /= np.abs(np.max(xx) - np.min(xx)) / xx.shape[0]
            #     params['distance'] = params['distance'] if params['distance'] >= 1. else 1.
            if params['widths'] is not None:
                params['widths'] /= np.abs(np.max(xx) - np.min(xx)) / xx.shape[0]

            result_idx = find_peaks_cwt(yy, **params)
            pos_xy = np.array([xx[result_idx], yy[result_idx]])
            # print(result_idx[1])
            self.q_app.set_peak_list(idx, (pos_xy, None))

    def on_btn_all(self):
        af = AutoFindPopUp(parent=self)
        af.exec()
