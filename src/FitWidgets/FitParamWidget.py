from PyQt5.QtWidgets import QWidget, QCheckBox, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from FitWidgets.FloatEditWidget import FloatEditWidget
import numpy as np


class FitParamWidget(QWidget):
    offset = 2
    check_w = 20
    label_w = None
    error_w = 80

    valueUpdated = pyqtSignal(float)

    def __init__(self, parent=None, *args, **kwargs):
        QWidget.__init__(self, parent=parent)

        name = kwargs.pop('name')
        value = kwargs.pop('value')
        error = kwargs.pop('error')
        self.label_w = kwargs.pop('label_w', self.label_w)

        self.optimize = QCheckBox(parent=self)
        name = QLabel(name + ' = ', parent=self)
        name.setAlignment(Qt.AlignRight)
        self.edit = FloatEditWidget(parent=self)
        self.edit.value = value
        self.error = QLabel('± %.03E' % error, parent=self)

        if self.label_w is None:
            self.label_w = name.sizeHint().width()
        self.optimize.setFixedWidth(self.check_w)
        name.setFixedWidth(self.label_w)
        self.error.setFixedWidth(self.error_w)

        self.optimize.move(0, 5)
        name.move(self.offset + self.check_w, 5)
        self.edit.move(2 * self.offset + self.check_w + self.label_w, 0)
        self.error.move(3 * self.offset + self.check_w + self.label_w + self.edit.width(), 5)
        self.setFixedWidth(4 * self.offset + self.check_w + self.label_w + self.edit.width() + self.error_w)
        self.setFixedHeight(self.edit.height())

        self.edit.valueUserUpd.connect(self.on_value_updated)

    def on_value_updated(self, nval):
        self.error.setText('± %.03E' % np.inf)
        self.valueUpdated.emit(nval)


if __name__ == '__main__':
    import sys
    from P61BApp import P61BApp

    q_app = P61BApp(sys.argv)
    app = FitParamWidget(name='Parameter', value=3.1E-2, error=np.inf)
    app.show()
    sys.exit(q_app.exec())
