from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton
import sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class PlotWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        line_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self._line_ax = line_canvas.figure.subplots()
        self._line_ax.set_xlabel('Energy, [keV]')
        self._line_ax.set_ylabel('Intensity, [counts]')

        # buttons
        autoscale_btn = QPushButton('A')
        autoscale_btn.clicked.connect(lambda *args: self.update_line_axes(autoscale=True))

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(line_canvas, 1, 1, 1, 2)
        layout.addWidget(autoscale_btn, 2, 1, 1, 1)
        layout.addWidget(NavigationToolbar(line_canvas, self), 2, 2, 1, 1)

    def clear_line_axes(self):
        del self._line_ax.lines[:]

    def axes_add_line(self, line):
        self._line_ax.add_line(line)

    def update_line_axes(self, autoscale=True):
        if autoscale:
            self._line_ax.autoscale()
        self._line_ax.figure.canvas.draw()


if __name__ == '__main__':
    q_app = QApplication(sys.argv)
    app = PlotWidget()
    app.show()
    sys.exit(q_app.exec_())
