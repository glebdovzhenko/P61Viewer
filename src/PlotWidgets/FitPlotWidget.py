from PyQt5.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from P61BApp import P61BApp


class FitPlotWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61BApp.instance()

        line_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self._line_ax = line_canvas.figure.subplots()
        self._line_ax.set_xlabel('Energy, [keV]')
        self._line_ax.set_ylabel('Intensity, [counts]')

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(line_canvas)

        self.q_app.plotXYLimChanged.connect(self.on_plot_lim_changed)
        self.q_app.selectedIndexChanged.connect(self.on_selected_active_changed)
        self.q_app.selectedIndexChanged.connect(self.on_selected_active_changed)

        # P61BApp.instance().project.selectedHistChanged.connect(self.on_selected_h_change)
        # P61BApp.instance().project.plotLimUpdated.connect(self.on_plot_lim_upd)

    def on_plot_lim_changed(self):
        self._line_ax.set_xlim(*self.q_app.params['PlotXLim'])
        self._line_ax.set_ylim(*self.q_app.params['PlotYLim'])
        self._line_ax.figure.canvas.draw()

    def on_selected_active_changed(self, idx):
        self.clear_line_axes()
        if idx != -1:
            data = self.q_app.data.loc[idx, ['DataX', 'DataY', 'Color', 'FitResult']]
            self._line_ax.plot(data['DataX'], data['DataY'], color=str(hex(data['Color'])).replace('0x', '#'),
                               marker='', linestyle='-')
            if data['FitResult'] is not None:
                xx = data['DataX']
                sel = (self.q_app.params['PlotXLim'][0] < xx) & (self.q_app.params['PlotXLim'][1] > xx)
                xx = xx[sel]

                self._line_ax.plot(xx, data['FitResult'].eval(data['FitResult'].params, x=xx),
                                   color=str(hex(next(self.q_app.params['ColorWheel2']))).replace('0x', '#'),
                                   marker='', linestyle='--')
                cmps = data['FitResult'].eval_components(x=xx)

                for cmp in cmps:
                    self._line_ax.plot(xx, cmps[cmp],
                                       color=str(hex(next(self.q_app.params['ColorWheel2']))).replace('0x', '#'),
                                       marker='', linestyle='--')
        self._line_ax.figure.canvas.draw()

    def clear_line_axes(self):
        del self._line_ax.lines[:]

    def axes_add_line(self, line):
        self._line_ax.add_line(line)


if __name__ == '__main__':
    from ListWidgets import EditableListWidget, ActiveListWidget
    import sys
    q_app = P61BApp(sys.argv)
    app = FitPlotWidget()
    app2 = EditableListWidget()
    app3 = ActiveListWidget()
    app.show()
    app2.show()
    app3.show()
    sys.exit(q_app.exec_())
