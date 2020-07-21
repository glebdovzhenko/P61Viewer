from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QDialog, QAbstractItemView, QProgressDialog
from PyQt5.Qt import Qt
from scipy.signal import find_peaks
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


class AutoFindWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.title_label = QLabel('Sample Peak Search')

        self.height_label = QLabel('Height')
        self.height_label.setToolTip('Required minimal height of peaks. Either a number or None.')
        self.height_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=1.)
        self.thr_label = QLabel('Threshhold')
        self.thr_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=None)
        self.dist_label = QLabel('Distance')
        self.dist_label.setToolTip('Required minimal horizontal distance between neighbouring peaks.\n'
                                   'Smaller peaks are removed first until the condition is fulfilled '
                                   'for all remaining peaks.')
        self.dist_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=8E-1)
        self.prom_label = QLabel('Prominence')
        self.prom_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=None)
        self.width_label = QLabel('Width')
        self.width_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=5E-2)
        self.width_label.setToolTip('Required minimal width of peaks. Either a number or None.')
        self.btn_this = QPushButton('Find')
        self.btn_all = QPushButton('Find in all')

        self.btn_this.clicked.connect(self.on_btn_this)
        self.btn_all.clicked.connect(self.on_btn_all)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.title_label, 1, 1, 1, 2)

        layout.addWidget(self.height_label, 2, 1, 1, 1)
        layout.addWidget(self.height_edit, 2, 2, 1, 1)

        layout.addWidget(self.dist_label, 3, 1, 1, 1)
        layout.addWidget(self.dist_edit, 3, 2, 1, 1)

        layout.addWidget(self.width_label, 4, 1, 1, 1)
        layout.addWidget(self.width_edit, 4, 2, 1, 1)

        layout.addWidget(self.thr_label, 5, 1, 1, 1)
        layout.addWidget(self.thr_edit, 5, 2, 1, 1)

        layout.addWidget(self.prom_label, 6, 1, 1, 1)
        layout.addWidget(self.prom_edit, 6, 2, 1, 1)

        layout.addWidget(self.btn_this, 7, 1, 1, 1)
        layout.addWidget(self.btn_all, 7, 2, 1, 1)

    def on_btn_this(self, *args, idx=-1):
        params = {
            'height': self.height_edit.get_value(),
            'threshold': self.thr_edit.get_value(),
            'distance': self.dist_edit.get_value(),
            'prominence': self.prom_edit.get_value(),
            'width': self.width_edit.get_value()
        }

        if idx == -1:
            idx = self.q_app.get_selected_idx()

        if idx != -1:
            yy = self.q_app.data.loc[idx, 'DataY']
            xx = self.q_app.data.loc[idx, 'DataX']

            if self.q_app.peak_search_range is not None:
                yy = yy[(xx < self.q_app.peak_search_range[1]) & (xx > self.q_app.peak_search_range[0])]
                xx = xx[(xx < self.q_app.peak_search_range[1]) & (xx > self.q_app.peak_search_range[0])]

            if params['distance'] is not None:
                params['distance'] /= np.abs(np.max(xx) - np.min(xx)) / xx.shape[0]
                params['distance'] = params['distance'] if params['distance'] >= 1. else 1.
            if params['width'] is not None:
                params['width'] /= np.abs(np.max(xx) - np.min(xx)) / xx.shape[0]

            for pp in params:
                if pp != 'distance' and params[pp] is None:
                    params[pp] = (None, None)

            result_idx = find_peaks(yy, **params)
            #  dict_keys(['peak_heights', 'left_thresholds', 'right_thresholds', 'prominences', 'left_bases',
            #  'right_bases', 'widths', 'width_heights', 'left_ips', 'right_ips'])
            pos_xy = np.array([xx[result_idx[0]], yy[result_idx[0]]])
            left_bases = xx[result_idx[1]['left_bases']]
            right_bases = xx[result_idx[1]['right_bases']]

            self.q_app.set_peak_list(idx, (pos_xy, {'left_bases': left_bases, 'right_bases': right_bases}))

    def on_btn_all(self):
        af = AutoFindPopUp(parent=self)
        af.exec()
