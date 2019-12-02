from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit
from PyQt5.QtCore import pyqtSignal
import re
import numpy as np

from P61App import P61App


class FloatEditWidget(QWidget):
    offset = 2
    button_w = 20
    edit_w = 80
    total_h = 25

    valueUserUpd = pyqtSignal(float)

    def __init__(self, value=0., value_min=-np.inf, value_max=np.inf, parent=None):
        QWidget.__init__(self, parent=parent)

        decrease = QPushButton('<', parent=self)
        self.edit = QLineEdit(parent=self)
        increase = QPushButton('>', parent=self)

        self.float_regexp = re.compile(r'^(?P<main>-?[0-9]+\.?)((?P<decimal>[0-9]+)([Ee](?P<exp>[+-]*[0-9]+))?)?$')

        self.value_min = value_min
        self.value_max = value_max
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

    def check_min_max(self, val):
        return self.value_max > val > self.value_min

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

    def set_value(self, val, emit=True):
        if not isinstance(val, (float, int)):
            raise ValueError()
        val = float(val)
        self.edit.setText('%.03E' % val)

        if emit:
            self.valueUserUpd.emit(val)

    def setValue(self, val):
        self.set_value(val, emit=False)

    def on_text_changed(self, *args):
        if not self.float_regexp.match(self.edit.text()):
            self.edit.setStyleSheet('QLineEdit {background-color: rgb(255, 70, 70);}')
        else:
            self.edit.setStyleSheet('QLineEdit {background-color: rgb(255, 255, 255);}')

    def on_text_submitted(self, *args):
        value = self.get_value()
        if value is not None:
            self.set_value(value)

    def _on_increase(self, *args):
        value = self.get_value()
        if value is not None:
            dv = abs(0.1 * value)
            self.set_value(value + dv)

    def _on_decrease(self, *args):
        value = self.get_value()
        if value is not None:
            dv = abs(0.1 * value)
            self.set_value(value - dv)

    value = property(fget=get_value, fset=set_value)


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = FloatEditWidget()
    app.show()
    sys.exit(q_app.exec())