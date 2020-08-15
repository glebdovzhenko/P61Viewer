from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout
import numpy as np
import scipy

from FitWidgets import LmfitInspector
from P61App import P61App


class PeakFitWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.btn_bckg = QPushButton('Interpolate background')
        self.btn_init = QPushButton('Initiate peak models')
        self.inspector = LmfitInspector(parent=self)

        self.btn_bckg.clicked.connect(self.on_interpolate)
        self.btn_init.clicked.connect(self.on_initiate)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.btn_bckg, 1, 1, 1, 1)
        layout.addWidget(self.btn_init, 2, 1, 1, 1)
        layout.addWidget(self.inspector, 3, 1, 1, 1)

    def on_initiate(self):
        pass

    def on_interpolate(self):
        idx = self.q_app.get_selected_idx()
        if idx == -1:
            return

        data = self.q_app.data.loc[idx, ['DataX', 'DataY', 'PeakList']]
        yy = data.loc['DataY']
        xx = data.loc['DataX']
        peak_list = self.q_app.get_stacked_peaks()
        if peak_list is None:
            peak_list = data.loc['PeakList']

        xx_orig = xx.copy()
        if peak_list is not None:
            for ta in peak_list:
                yy = yy[(xx < ta['area'][0]) | (xx > ta['area'][1])]
                xx = xx[(xx < ta['area'][0]) | (xx > ta['area'][1])]

        f = scipy.interpolate.interp1d(xx, yy)
        self.q_app.set_bckg_interp(idx, f(xx_orig))



