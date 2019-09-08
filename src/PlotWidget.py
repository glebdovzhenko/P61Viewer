from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
import sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import numpy as np


class PlotWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent=parent)

        layout = QVBoxLayout()

        line_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self._line_ax = line_canvas.figure.subplots()
        self._line_ax.set_xlabel('Energy, [keV]')
        self._line_ax.set_ylabel('Intensity, [counts]')

        layout.addWidget(line_canvas)
        layout.addWidget(NavigationToolbar(line_canvas, self))
        self.setLayout(layout)


if __name__ == '__main__':
    qapp = QApplication(sys.argv)
    app = PlotWidget()
    app.show()
    sys.exit(qapp.exec_())
