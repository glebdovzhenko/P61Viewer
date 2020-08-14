from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QDialog, QAbstractItemView, QProgressDialog
from PyQt5.Qt import Qt
from scipy.signal import find_peaks
import numpy as np
from functools import reduce
from copy import deepcopy

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
        progress.setWindowModality(Qt.ApplicationModal)

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
        self.height_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=20.)
        self.thr_label = QLabel('Threshhold')
        self.thr_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=None)
        self.dist_label = QLabel('Distance')
        self.dist_label.setToolTip('Required minimal horizontal distance between neighbouring peaks.\n'
                                   'Smaller peaks are removed first until the condition is fulfilled '
                                   'for all remaining peaks.')
        self.dist_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=5E-1)
        self.prom_label = QLabel('Prominence')
        self.prom_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=10.)
        self.width_label = QLabel('Width')
        self.width_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=5E-2)
        self.width_label.setToolTip('Required minimal width of peaks. Either a number or None.')
        self.cutoff_label = QLabel('Cutoff')
        self.cutoff_edit = FloatEdit(inf_allowed=True, none_allowed=True, init_val=3.)
        self.cutoff_label.setToolTip('Peak base cutoff measured in sigmas.')
        self.tw_label = QLabel('Track window')
        self.tw_edit = FloatEdit(inf_allowed=False, none_allowed=True, init_val=1E-1)
        self.tw_label.setToolTip('Max peak shift between the spectra.')
        self.btn_this = QPushButton('Find')
        self.btn_all = QPushButton('Find in all')
        self.btn_stack = QPushButton('Stack peaks')

        self.btn_this.clicked.connect(self.on_btn_this)
        self.btn_all.clicked.connect(self.on_btn_all)
        self.btn_stack.clicked.connect(self.on_btn_stack)

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

        layout.addWidget(self.cutoff_label, 7, 1, 1, 1)
        layout.addWidget(self.cutoff_edit, 7, 2, 1, 1)

        layout.addWidget(self.btn_this, 8, 1, 1, 1)
        layout.addWidget(self.btn_all, 8, 2, 1, 1)

        layout.addWidget(self.tw_label, 9, 1, 1, 1)
        layout.addWidget(self.tw_edit, 9, 2, 1, 1)

        layout.addWidget(self.btn_stack, 10, 1, 1, 2)

    def on_btn_stack(self):
        idx = self.q_app.get_selected_idx()
        if idx == -1:
            return

        tw = self.tw_edit.get_value()

        peak_list = reduce(lambda a, b: a + b,
                           filter(lambda x: x is not None,
                                  self.q_app.data.loc[self.q_app.get_active_ids(), 'PeakList']),
                           [])
        peak_list = deepcopy(peak_list)
        for _ in range(2):  # stupid but I'll fix it later
            for ii, ta in enumerate(peak_list):
                for ii2 in range(len(peak_list) - 1, ii, -1):
                    ta2 = peak_list[ii2]
                    if (ta2['area'][0] <= ta['area'][0] <= ta2['area'][1]) or \
                        (ta2['area'][0] <= ta['area'][1] <= ta2['area'][1]) or \
                            (ta['area'][0] <= ta2['area'][0] and ta['area'][1] >= ta2['area'][1]):

                        ta['area'] = (min(ta['area'][0], ta2['area'][0]),
                                      max(ta['area'][1], ta2['area'][1]))

                        for p2 in ta2['peaks']:
                            for p in ta['peaks']:
                                if np.abs(p['center_x'] - p2['center_x']) <= tw:
                                    break
                            else:
                                ta['peaks'] += (p2, )
                        peak_list.pop(ii2)

        self.q_app.stacked_peaks = peak_list

    def on_btn_this(self, *args, idx=-1):
        params = {
            'height': self.height_edit.get_value(),
            'threshold': self.thr_edit.get_value(),
            'distance': self.dist_edit.get_value(),
            'prominence': self.prom_edit.get_value(),
            'width': self.width_edit.get_value()
        }
        cutoff = self.cutoff_edit.get_value()

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
            pos_x = xx[result_idx[0]]
            pos_y = yy[result_idx[0]]
            left_ips = np.interp(result_idx[1]['left_ips'], np.arange(0, xx.shape[0]), xx)
            right_ips = np.interp(result_idx[1]['right_ips'], np.arange(0, xx.shape[0]), xx)
            width_heights = result_idx[1]['width_heights']

            if cutoff < np.inf:
                g_sigmas = (right_ips - left_ips) / (2. * np.sqrt(2. * np.log(2)))
                left_bases = pos_x - cutoff * g_sigmas
                right_bases = pos_x + cutoff * g_sigmas
            else:
                left_bases = xx[result_idx[1]['left_bases']]
                right_bases = xx[result_idx[1]['right_bases']]

            track_areas = []
            sort_ids = np.argsort(left_bases)

            for lb, rb, li, ri, wh, cx, cy in zip(left_bases[sort_ids], right_bases[sort_ids], left_ips[sort_ids],
                                                  right_ips[sort_ids], width_heights[sort_ids], pos_x[sort_ids],
                                                  pos_y[sort_ids]):
                for ta in track_areas:
                    if lb < ta['area'][1]:
                        ta['area'] = (ta['area'][0], max(ta['area'][1], rb))
                        ta['peaks'] += ({'center_x': cx, 'center_y': cy, 'width_height': wh,
                                         'left_ip': li, 'right_ip': ri}, )
                        break
                else:
                    track_areas.append({'area': (lb, rb), 'peaks': ({'center_x': cx, 'center_y': cy, 'width_height': wh,
                                                                     'left_ip': li, 'right_ip': ri}, )})

            self.q_app.set_peak_list(idx, track_areas)

    def on_btn_all(self):
        af = AutoFindPopUp(parent=self)
        af.exec()
