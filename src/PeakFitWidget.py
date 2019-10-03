from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLineEdit, QGridLayout, QLabel, QCheckBox, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt
import re

from PeakFit import GaussianFit, LorentzianFit, PsVoigtFit


class FloatEdit(QWidget):
    offset = 2
    button_w = 20
    edit_w = 80
    total_h = 25

    returnPressed = pyqtSignal()

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args)

        decrease = QPushButton('<', parent=self)
        self.edit = QLineEdit(parent=self)
        increase = QPushButton('>', parent=self)

        self.float_regexp = re.compile(r'^(?P<main>-?[0-9]+\.?)((?P<decimal>[0-9]+)([Ee](?P<exp>[+-]*[0-9]+))?)?$')

        value = kwargs.pop('value')
        self.set_value(value)

        decrease.setFixedWidth(self.button_w)
        decrease.setFixedHeight(self.total_h)
        decrease.move(0, 0)

        self.edit.setFixedWidth(self.edit_w)
        self.edit.setFixedHeight(self.total_h)
        self.edit.move(self.button_w + self.offset, 0)

        increase.setFixedWidth(self.button_w)
        increase.setFixedHeight(self.total_h)
        increase.move(self.button_w + 2 * self.offset + self.edit_w, 0)

        self.setFixedWidth(4 * self.offset + 2 * self.button_w + self.edit_w)
        self.setFixedHeight(self.total_h)

        self.edit.textChanged.connect(self.on_text_changed)
        self.edit.returnPressed.connect(self.on_text_submitted)
        self.edit.editingFinished.connect(self.on_text_submitted)

        increase.clicked.connect(self._on_increase)
        decrease.clicked.connect(self._on_decrease)

    def get_value(self):
        m = self.float_regexp.match(self.edit.text())
        if not m:
            self.edit.setStyleSheet('QLineEdit {background-color: rgb(255, 0, 0);}')
            return None
        else:
            gd = m.groupdict()
            value = float(gd['main'])
            if gd['decimal'] is not None:
                value += (float(gd['decimal']) if value >= 0 else -float(gd['decimal'])) * 10 ** (-len(gd['decimal']))
            if gd['exp'] is not None:
                value *= 10 ** (int(gd['exp']))
            return value

    def set_value(self, val):
        if not isinstance(val, (float, int)):
            raise ValueError()
        self.edit.setText('%.03E' % val)
        self.returnPressed.emit()

    def on_text_changed(self):
        if not self.float_regexp.match(self.edit.text()):
            self.edit.setStyleSheet('QLineEdit {background-color: rgb(255, 70, 70);}')
        else:
            self.edit.setStyleSheet('QLineEdit {background-color: rgb(255, 255, 255);}')

    def on_text_submitted(self):
        value = self.get_value()
        if value is not None:
            self.set_value(value)

    def _on_increase(self):
        value = self.get_value()
        if value is not None:
            dv = abs(0.1 * value)
            self.set_value(value + dv)

    def _on_decrease(self):
        value = self.get_value()
        if value is not None:
            dv = abs(0.1 * value)
            self.set_value(value - dv)

    value = property(fget=get_value, fset=set_value)


class FitParamWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args)

        name = kwargs.pop('name')
        value = kwargs.pop('value')
        error = kwargs.pop('error')

        optimize = QCheckBox()
        name = QLabel(name + ' = ')
        edit = FloatEdit(value=value)
        error = QLabel('± %.03E' % error)

        optimize.setFixedWidth(20)
        # label.setAlignment(Qt.AlignRight)
        name.setFixedWidth(25)

        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(optimize)
        layout.addWidget(name)
        layout.addWidget(edit)
        layout.addWidget(error)
        self.setFixedWidth(300)


class PeakFitWidget(QWidget):
    imgs = {GaussianFit: '../img/gaussian_eq.png',
            LorentzianFit: '../img/lorentzian_eq.png',
            PsVoigtFit: '../img/pvoigt_eq.png'}

    def __init__(self, parent=None, **kwargs):

        if 'fitter' in kwargs:
            self.peak_fit_cls = kwargs.pop('fitter')

        super().__init__(parent, *kwargs)

        # fit area left border changer
        area_left = FloatEdit(value=0)
        area_right = FloatEdit(value=1)
        area_label = QLabel('Selected area')
        area_label.setFixedWidth(100)

        # fit area right border changer

        # function label
        function_label = QLabel()
        pm = QPixmap(self.imgs[self.peak_fit_cls])
        function_label.setPixmap(pm)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(area_left, 1, 1, 1, 1)
        layout.addWidget(area_label, 1, 2, 1, 1)
        layout.addWidget(area_right, 1, 3, 1, 1)
        layout.addWidget(function_label, 2, 1, 1, 4)

        for i, name in enumerate(self.peak_fit_cls.param_names):
            layout.addWidget(FitParamWidget(name=name, value=i, error=0), 3 + i, 1, 1, 7)


if __name__ == '__main__':
    import sys
    q_app = QApplication(sys.argv)
    app = PeakFitWidget(fitter=PsVoigtFit)
    app.show()
    sys.exit(q_app.exec_())
