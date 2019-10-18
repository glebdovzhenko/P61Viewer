from PyQt5.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from P61BApp import P61BApp


class MainPlotWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        line_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self._line_ax = line_canvas.figure.subplots()
        self._line_ax.set_xlabel('Energy, [keV]')
        self._line_ax.set_ylabel('Intensity, [counts]')

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(line_canvas)
        layout.addWidget(NavigationToolbar(line_canvas, self))

        P61BApp.instance().project.histsAdded.connect(self.on_hists_added)
        P61BApp.instance().project.histsRemoved.connect(self.on_hists_removed)
        P61BApp.instance().project.histsActiveChanged.connect(self.on_hists_ac)

    def clear_line_axes(self):
        del self._line_ax.lines[:]

    def axes_add_line(self, line):
        self._line_ax.add_line(line)

    def update_line_axes(self, autoscale=True):
        if autoscale:
            self._line_ax.autoscale()
            self._line_ax.figure.canvas.toolbar.update()
        self._line_ax.figure.canvas.draw()

    def on_hists_added(self):
        self.clear_line_axes()
        for line in P61BApp.instance().project.get_plot_lines():
            self.axes_add_line(line)
        self.update_line_axes()

    def on_hists_removed(self):
        self.clear_line_axes()
        for line in P61BApp.instance().project.get_plot_lines():
            self.axes_add_line(line)
        self.update_line_axes(autoscale=False)

    def on_hists_ac(self):
        self.clear_line_axes()
        for line in P61BApp.instance().project.get_plot_lines():
            self.axes_add_line(line)
        self.update_line_axes(autoscale=False)


if __name__ == '__main__':
    from ListWidgets import EditableListWidget
    import sys
    q_app = P61BApp(sys.argv)
    app = MainPlotWidget()
    app2 = EditableListWidget()
    app.show()
    app2.show()
    sys.exit(q_app.exec_())
