from PyQt5.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import numpy as np

from .MainPlotWidget import MainPlotWidget
from P61App import P61App


class PeakFitPlotWidget(MainPlotWidget):
    def __init__(self, parent=None):
        MainPlotWidget.__init__(self, parent=parent)

        self._line_ax.figure.canvas.mpl_connect('button_press_event', self.on_mouse_click)

    def on_mouse_click(self, event):
        if event.inaxes == self._line_ax:
            print(event.xdata, event.ydata)


if __name__ == '__main__':
    from ListWidgets import EditableListWidget, ActiveListWidget
    import sys
    q_app = P61App(sys.argv)
    app = PeakFitPlotWidget()
    app2 = EditableListWidget()
    app3 = ActiveListWidget()
    app.show()
    app2.show()
    app3.show()
    sys.exit(q_app.exec_())
