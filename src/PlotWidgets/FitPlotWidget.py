from PyQt5.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from P61App import P61App


class FitPlotWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        line_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self._line_ax, self._diff_ax = line_canvas.figure.subplots(nrows=2, ncols=1, sharex=True,
                                                                   gridspec_kw={'height_ratios': [4, 1]})
        self._diff_ax.set_xlabel('Energy, [keV]')
        self._line_ax.set_ylabel('Intensity, [counts]')

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(line_canvas)

        self.q_app.plotXYLimChanged.connect(self.on_plot_lim_changed)
        self.q_app.selectedIndexChanged.connect(self.on_selected_active_changed)

        # P61App.instance().project.selectedHistChanged.connect(self.on_selected_h_change)
        # P61App.instance().project.plotLimUpdated.connect(self.on_plot_lim_upd)

    def on_plot_lim_changed(self):
        self._line_ax.set_xlim(*self.q_app.params['PlotXLim'])
        self._line_ax.set_ylim(*self.q_app.params['PlotYLim'])
        self._line_ax.figure.canvas.draw()

    def on_selected_active_changed(self, idx):
        self.clear_axes()
        if idx != -1:
            data = self.q_app.data.loc[idx, ['DataX', 'DataY', 'Color', 'FitResult']]
            self._line_ax.plot(data['DataX'], data['DataY'], color='black', marker='.', linestyle='')
            if data['FitResult'] is not None:
                xx = data['DataX']
                sel = (self.q_app.params['PlotXLim'][0] < xx) & (self.q_app.params['PlotXLim'][1] > xx)
                xx = xx[sel]
                yy = data['DataY'][sel]

                self._line_ax.plot(xx, data['FitResult'].eval(data['FitResult'].params, x=xx),
                                   color='#d62728', marker='', linestyle='--')
                tmp = yy - data['FitResult'].eval(data['FitResult'].params, x=xx)
                self._diff_ax.plot(xx, tmp, color='#d62728', marker='', linestyle='--')
                self._diff_ax.set_ylim(min(tmp) - 0.1 * abs(max(tmp) - min(tmp)),
                                       max(tmp) + 0.1 * abs(max(tmp) - min(tmp)))
                cmps = data['FitResult'].eval_components(x=xx)

                for cmp in cmps:
                    self._line_ax.plot(xx, cmps[cmp],
                                       color=str(hex(next(self.q_app.params['ColorWheel2']))).replace('0x', '#'),
                                       marker='', linestyle='--')
        self._line_ax.figure.canvas.draw()
        self._diff_ax.figure.canvas.draw()

    def clear_axes(self):
        del self._line_ax.lines[:]
        del self._diff_ax.lines[:]

    # def axes_add_line(self, line):
    #     self._line_ax.add_line(line)


if __name__ == '__main__':
    from ListWidgets import EditableListWidget, ActiveListWidget
    import sys
    q_app = P61App(sys.argv)
    app = FitPlotWidget()
    app2 = EditableListWidget()
    app3 = ActiveListWidget()
    app.show()
    app2.show()
    app3.show()
    sys.exit(q_app.exec_())
