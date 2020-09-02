from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton, QLabel
import copy
import numpy as np
import logging

from P61App import P61App
from DatasetManager import DatasetSelector
from FitWidgets.FloatEdit import FloatEdit
from lmfit_utils import constrain_params


class ConstrainPopUp(QDialog):
    """"""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        self.q_app = P61App.instance()
        self.logger = logging.getLogger(str(self.__class__))

        self.sigma_expl_format = u'σ variation from %.01f to %.01f means that\n' +\
                                 u'during minimization the σ value\n' +\
                                 u'of each peak will be varied\n' +\
                                 u'from %.01f to %.01f of its current value.'

        self.center_expl_format = u'Center variation of %.03f means that\n' +\
                                  u'during minimization center position\n' +\
                                  u'of each peak will be varied\n' +\
                                  u'from (c - %.03fσ) to (c + %.03fσ).'

        self.label_selector = QLabel('Datasets:')
        self.list_to = DatasetSelector(parent=self)
        self.button_ok = QPushButton('Apply')

        self.height_label = QLabel('Min and max height values:')
        self.height_min = FloatEdit(inf_allowed=False, none_allowed=True, init_val=0.)
        self.height_max = FloatEdit(inf_allowed=False, none_allowed=True, init_val=1E3)

        self.center_label = QLabel('Center variation:')
        self.center_vary = FloatEdit(inf_allowed=False, none_allowed=False, init_val=0.25)
        self.center_expl = QLabel(self.center_expl_format % (0.25, 0.125, 0.125))

        self.sigma_label = QLabel('σ variation:')
        self.sigma_min = FloatEdit(inf_allowed=False, none_allowed=True, init_val=0.9)
        self.sigma_max = FloatEdit(inf_allowed=False, none_allowed=True, init_val=1.1)
        self.sigma_expl = QLabel(self.sigma_expl_format % (0.9, 1.1, 0.9, 1.1))

        self.setWindowTitle('Constrain minimization parameters')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.label_selector, 1, 1, 1, 1)
        layout.addWidget(self.list_to, 2, 1, 8, 1)

        layout.addWidget(self.height_label, 2, 2, 1, 2)
        layout.addWidget(self.height_min, 3, 2, 1, 1)
        layout.addWidget(self.height_max, 3, 3, 1, 1)

        layout.addWidget(self.center_label, 4, 2, 1, 2)
        layout.addWidget(self.center_vary, 5, 2, 1, 2)
        layout.addWidget(self.center_expl, 6, 2, 1, 2)

        layout.addWidget(self.sigma_label, 7, 2, 1, 2)
        layout.addWidget(self.sigma_min, 8, 2, 1, 1)
        layout.addWidget(self.sigma_max, 8, 3, 1, 1)
        layout.addWidget(self.sigma_expl, 9, 2, 1, 2)

        layout.addWidget(self.button_ok, 10, 2, 1, 1)

        self.button_ok.clicked.connect(self.on_button_ok)
        self.center_vary.valueChanged.connect(self._on_center_vc)

    def _on_center_vc(self, n_val):
        if n_val is None:
            pass
        else:
            self.center_expl.setText(self.center_expl_format % (n_val, .5 * n_val, .5 * n_val))

    def on_button_ok(self):
        ids = [k for k in self.list_to.proxy.selected if self.list_to.proxy.selected[k]]

        for idx in ids:
            md = self.q_app.get_general_result(idx)
            if md is None:
                continue

            md = constrain_params(md, self.center_vary.value, self.height_min.value, self.height_max.value,
                                  self.sigma_min.value, self.sigma_max.value)

            self.q_app.set_general_result(idx, md)
        self.close()


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = ConstrainPopUp()
    app.show()
    sys.exit(q_app.exec())