from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLineEdit, QGridLayout, QLabel, QCheckBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from src.PeakFit import GaussianFit, LorentzianFit, PsVoigtFit


class PeakFitWidget(QWidget):
    imgs = {GaussianFit: '../img/gaussian_eq.png',
            LorentzianFit: '../img/lorentzian_eq.png',
            PsVoigtFit: '../img/pvoigt_eq.png'}

    def __init__(self, parent=None, **kwargs):

        if 'fitter' in kwargs:
            self.peak_fit_cls = kwargs.pop('fitter')

        super().__init__(parent, *kwargs)

        # fit area left border changer
        area_left_minus = QPushButton('<')
        area_left_value = QLineEdit()
        area_left_value.setFixedWidth(40)
        area_left_plus = QPushButton('>')

        area_label = QLabel('Selected area')
        area_label.setFixedWidth(100)

        # fit area right border changer
        area_right_minus = QPushButton('<')
        area_right_value = QLineEdit()
        area_right_value.setFixedWidth(40)
        area_right_plus = QPushButton('>')

        # function label
        function_label = QLabel()
        pm = QPixmap(self.imgs[self.peak_fit_cls])
        function_label.setPixmap(pm)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(area_left_minus, 1, 1, 1, 1)
        layout.addWidget(area_left_value, 1, 2, 1, 1)
        layout.addWidget(area_left_plus, 1, 3, 1, 1)
        layout.addWidget(area_label, 1, 4, 1, 1)
        layout.addWidget(area_right_minus, 1, 5, 1, 1)
        layout.addWidget(area_right_value, 1, 6, 1, 1)
        layout.addWidget(area_right_plus, 1, 7, 1, 1)
        layout.addWidget(function_label, 2, 1, 1, 7)

        for i, name in enumerate(self.peak_fit_cls.param_names):
            cb = QCheckBox()
            l = QLabel('  ' + name + ' ' * (4 - len(name)))
            bm = QPushButton('<')
            bp = QPushButton('>')
            v = QLineEdit()
            v.setFixedWidth(40)
            tmp_l = QHBoxLayout()
            tmp_l.addWidget(cb)
            tmp_l.addWidget(l)
            tmp_l.addWidget(bm)
            tmp_l.addWidget(v)
            tmp_l.addWidget(bp)
            tmp_l.addStretch(1)
            layout.addLayout(tmp_l, 3 + i, 1, 1, 7)


if __name__ == '__main__':
    import sys
    q_app = QApplication(sys.argv)
    app = PeakFitWidget(fitter=PsVoigtFit)
    app.show()
    sys.exit(q_app.exec_())
