from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPixmap
import numpy as np

from FitWidgets.FitParamWidget import FitParamWidget


class FunctionReprWidget(QWidget):
    img_path = ''
    params = ()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        function_label = QLabel(parent=self)
        function_label.setPixmap(QPixmap(self.img_path))
        function_label.setFixedWidth(function_label.sizeHint().width() + 8)
        function_label.move(4, 0)

        self.param_widgets = dict()
        for ii, k in enumerate(self.params):
            self.param_widgets[k] = FitParamWidget(parent=self, name=k, value=0.0, error=np.inf, label_w=30)
            self.param_widgets[k].move(4, 30 * ii + function_label.sizeHint().height() + 8)
        else:
            self.setFixedHeight(30 * (ii + 1) + function_label.sizeHint().height() + 10)

        self.setFixedWidth(function_label.width())


class GaussianReprWidget(FunctionReprWidget):
    img_path = '../../img/gaussian_eq.png'
    params = ('A', 'x0', 's', 'a', 'b')


class LorentzianReprWidget(FunctionReprWidget):
    img_path = '../../img/lorentzian_eq.png'
    params = ('A', 'x0', 'g', 'a', 'b')


class PVoigtReprWidget(FunctionReprWidget):
    img_path = '../../img/pvoigt_eq2.png'
    params = ('A', 'n', 'x0', 'g', 's', 'a', 'b')


if __name__ == '__main__':
    import sys
    from P61BApp import P61BApp
    q_app = P61BApp(sys.argv)
    w1 = GaussianReprWidget()
    w1.show()
    w2 = LorentzianReprWidget()
    w2.show()
    w3 = PVoigtReprWidget()
    w3.show()
    sys.exit(q_app.exec())