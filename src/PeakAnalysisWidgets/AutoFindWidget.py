from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton
from scipy.signal import find_peaks
import numpy as np

from P61App import P61App
from FitWidgets.FloatEditWidget import FloatEditWidget


class AutoFindWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.title_label = QLabel('Automatic Peak Search')

        self.height_label = QLabel('Height')
        self.height_edit = FloatEditWidget(inf_allowed=False, none_allowed=True, init_val=1000.)
        self.thr_label = QLabel('Threshhold')
        self.thr_edit = FloatEditWidget(inf_allowed=False, none_allowed=True, init_val=None)
        self.dist_label = QLabel('Distance')
        self.dist_edit = FloatEditWidget(inf_allowed=False, none_allowed=True, init_val=None)
        self.prom_label = QLabel('Prominence')
        self.prom_edit = FloatEditWidget(inf_allowed=False, none_allowed=True, init_val=None)
        self.width_label = QLabel('Width')
        self.width_edit = FloatEditWidget(inf_allowed=False, none_allowed=True, init_val=None)
        self.btn_this = QPushButton('Find')
        self.btn_all = QPushButton('Find in all')

        self.btn_this.clicked.connect(self.on_btn_this)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.title_label, 1, 1, 1, 4)
        layout.addWidget(self.height_label, 2, 1, 1, 1)
        layout.addWidget(self.thr_label, 3, 1, 1, 1)
        layout.addWidget(self.dist_label, 4, 1, 1, 1)
        layout.addWidget(self.prom_label, 2, 3, 1, 1)
        layout.addWidget(self.width_label, 3, 3, 1, 1)
        layout.addWidget(self.height_edit, 2, 2, 1, 1)
        layout.addWidget(self.thr_edit, 3, 2, 1, 1)
        layout.addWidget(self.dist_edit, 4, 2, 1, 1)
        layout.addWidget(self.prom_edit, 2, 4, 1, 2)
        layout.addWidget(self.width_edit, 3, 4, 1, 2)
        layout.addWidget(self.btn_this, 5, 1, 1, 2)
        layout.addWidget(self.btn_all, 5, 3, 1, 2)

    def on_btn_this(self):
        params = {
            'height': self.height_edit.get_value(),
            'threshold': self.thr_edit.get_value(),
            'distance': self.dist_edit.get_value(),
            'prominence': self.prom_edit.get_value(),
            'width': self.width_edit.get_value()
        }

        idx = self.q_app.get_selected_idx()
        if idx != -1:
            yy = self.q_app.data.loc[idx, 'DataY']
            xx = self.q_app.data.loc[idx, 'DataX']
            if params['distance'] is not None:
                params['distance'] /= np.abs(np.max(xx) - np.min(xx)) / xx.shape[0]
                params['distance'] = params['distance'] if params['distance'] >= 1. else 1.
            if params['width'] is not None:
                params['width'] /= np.abs(np.max(xx) - np.min(xx)) / xx.shape[0]
            peaks, _ = find_peaks(yy, **params)
            self.q_app.set_peak_list(idx, peaks)