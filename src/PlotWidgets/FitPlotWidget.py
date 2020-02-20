from PyQt5.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import numpy as np

from P61App import P61App


class FitPlotWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        line_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self._line_ax, self._diff_ax = line_canvas.figure.subplots(nrows=2, ncols=1, sharex=True,
                                                                   gridspec_kw={'height_ratios': [4, 1]})
        self._diff_ax.set_xlabel('Energy, [keV]')
        self._diff_ax.set_ylabel('Difference [counts]')
        self._line_ax.set_ylabel('Intensity, [counts]')

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(line_canvas)
        layout.addWidget(NavigationToolbar(line_canvas, self))

        self.q_app.selectedIndexChanged.connect(self.on_selected_active_changed)
        self.q_app.dataFitChanged.connect(self.on_fit_changed)

    def on_fit_changed(self, idxs):
        if self.q_app.params['SelectedIndex'] in idxs:
            self.on_selected_active_changed(self.q_app.params['SelectedIndex'])

    def on_selected_active_changed(self, idx):
        self.clear_axes()
        if idx != -1:
            data = self.q_app.data.loc[idx, ['DataX', 'DataY', 'Color', 'FitResult']]
            self._line_ax.plot(data['DataX'], data['DataY'], color='black', marker='.', linestyle='', label='Data')
            if data['FitResult'] is not None:
                xx = data['DataX']
                x_lim = self.get_axes_xlim()
                sel = (x_lim[0] < xx) & (x_lim[1] > xx)
                xx = xx[sel]
                yy = data['DataY'][sel]
                diff = yy - data['FitResult'].eval(data['FitResult'].params, x=xx)

                cmps = data['FitResult'].eval_components(x=xx)
                for cmp in cmps:
                    if cmp not in self.q_app.params['LmFitModelColors'].keys():
                        self.q_app.params['LmFitModelColors'][cmp] = next(self.q_app.params['ColorWheel2'])
                    self._line_ax.plot(xx, cmps[cmp],
                                       color=str(hex(self.q_app.params['LmFitModelColors'][cmp])).replace('0x', '#'),
                                       marker='', linestyle='--', label=cmp)

                self._line_ax.plot(xx, data['FitResult'].eval(data['FitResult'].params, x=xx),
                                   color='#d62728', marker='', linestyle='--', label='Fit')
                self._diff_ax.plot(xx, diff, color='#d62728', marker='', linestyle='--')

            self._line_ax.legend()

        self.set_axes_ylim()
        self._line_ax.figure.canvas.draw()
        self._diff_ax.figure.canvas.draw()

    def clear_axes(self):
        del self._line_ax.lines[:]
        del self._diff_ax.lines[:]

    def get_axes_xlim(self):
        return self._line_ax.get_xlim()

    def set_axes_ylim(self):
        for ax in (self._line_ax, self._diff_ax):
            ydata = np.array(sum([list(line.get_ydata()) for line in ax.lines], []))
            ydata = ydata[~np.isnan(ydata)]
            ydata = ydata[~np.isinf(ydata)]
            if len(ydata):
                mi_, ma_ = np.min(ydata), np.max(ydata)
                ax.set_ylim(mi_ - 0.1 * abs(ma_ - mi_), ma_ + 0.1 * abs(ma_ - mi_))
            else:
                ax.set_ylim(0., 1.)


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
