from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
import sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


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

    def clear_line_axes(self):
        self._line_ax.clear()
        self._line_ax.set_xlabel('Energy, [keV]')
        self._line_ax.set_ylabel('Intensity, [counts]')

    def plot_line_axes(self, *args):
        return self._line_ax.plot(*args)

    def update_line_axes(self):
        self._line_ax.figure.canvas.draw()


if __name__ == '__main__':
    q_app = QApplication(sys.argv)
    app = PlotWidget()
    app.show()
    sys.exit(q_app.exec_())
