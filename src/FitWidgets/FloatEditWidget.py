from PyQt5.QtWidgets import QLineEdit
import re
import numpy as np


class FloatEditWidget(QLineEdit):
    """"""
    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent=parent)

        self.float_regexp = re.compile(
            r'^(?P<main>-?[0-9]+\.?)(?P<decimal>[0-9]+)?([Ee](?P<exp>[+-]{0,1}[0-9]+))?$|'
            r'^(?P<inf>\s*INF|inf|-INF|-inf\s*)$'
        )
        self._value = 0.

        self.textChanged.connect(self.on_text_changed)
        self.returnPressed.connect(self.on_text_submitted)
        self.editingFinished.connect(self.on_text_submitted)

    def on_text_changed(self):
        match = self.float_regexp.match(self.text())
        if not match:
            self.setStyleSheet('QLineEdit {background-color: rgb(255, 70, 70);}')
            return None
        else:
            self.setStyleSheet('QLineEdit {background-color: rgb(255, 255, 255);}')
            return match

    def on_text_submitted(self):
        match = self.on_text_changed()
        if match:
            gd = match.groupdict()
            if gd['inf'] is not None:
                self._value = np.float(gd['inf'])
            elif gd['main'] is not None:
                self._value = float(gd['main'])
                if gd['decimal'] is not None:
                    self._value += (float(gd['decimal']) if self._value >= 0
                                    else -float(gd['decimal'])) * 10 ** (-len(gd['decimal']))
                if gd['exp'] is not None:
                    self._value *= 10 ** (int(gd['exp']))
            self.setText('%.03E' % self._value)

    def get_value(self):
        return self._value

    def set_value(self, val):
        if not isinstance(val, (int, float, np.int, np.float)):
            raise ValueError(val, 'is not any of the', (int, float, np.int, np.float), 'types')
        else:
            self._value = val
            self.setText('%.03E' % self._value)

    value = property(fget=get_value, fset=set_value)


if __name__ == '__main__':
    from P61App import P61App
    import sys
    q_app = P61App(sys.argv)
    app = FloatEditWidget()
    app.value = 10
    app.show()
    sys.exit(q_app.exec())