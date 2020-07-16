from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.Qt import Qt
import pyqtgraph as pg

from P61App import P61App


class FitPlot(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'w')

        graph_widget = pg.GraphicsLayoutWidget(show=True)
        self._line_ax = graph_widget.addPlot(title="Fit")
        self._line_ax.setLabel('bottom', "Energy", units='eV')
        self._line_ax.setLabel('left', "Intensity", units='counts')
        self._line_ax.showGrid(x=True, y=True)
        graph_widget.nextRow()
        self._diff_ax = graph_widget.addPlot(title="Difference plot")
        self._diff_ax.setLabel('bottom', "Energy", units='eV')
        self._diff_ax.setLabel('left', "Intensity", units='counts')
        self._diff_ax.showGrid(x=True, y=True)
        self._diff_ax.setXLink(self._line_ax)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(graph_widget)

        self.q_app.selectedIndexChanged.connect(self.on_selected_active_changed)
        self.q_app.genFitResChanged.connect(self.on_fit_changed)

    def on_fit_changed(self, idxs):
        if self.q_app.get_selected_idx() in idxs:
            self.on_selected_active_changed(self.q_app.get_selected_idx())

    def on_selected_active_changed(self, idx):
        self.clear_axes()
        self._line_ax.addLegend()
        if idx != -1:
            data = self.q_app.data.loc[idx, ['DataX', 'DataY', 'Color', 'GeneralFitResult']]

            self._line_ax.plot(1E3 * data['DataX'], data['DataY'],
                               pen=pg.mkPen(color='#000000', style=Qt.DotLine), name='Data')

            if data['GeneralFitResult'] is not None:
                xx = data['DataX']
                x_lim = self.get_axes_xlim()
                sel = (x_lim[0] < xx) & (x_lim[1] > xx)
                xx = xx[sel]
                yy = data['DataY'][sel]
                diff = yy - data['GeneralFitResult'].eval(data['GeneralFitResult'].params, x=xx)

                cmps = data['GeneralFitResult'].eval_components(x=xx)
                for cmp in cmps:
                    if cmp not in self.q_app.params['LmFitModelColors'].keys():
                        self.q_app.params['LmFitModelColors'][cmp] = next(self.q_app.params['ColorWheel2'])
                    self._line_ax.plot(1E3 * xx, cmps[cmp], pen=pg.mkPen(
                        color=str(hex(self.q_app.params['LmFitModelColors'][cmp])).replace('0x', '#')),
                                       name=cmp)  # label=cmp

                self._line_ax.plot(1E3 * xx, data['GeneralFitResult'].eval(data['GeneralFitResult'].params, x=xx),
                                   pen=pg.mkPen(color='#d62728'), name='Fit')
                self._diff_ax.plot(1E3 * xx, diff, pen=pg.mkPen(color='#d62728'))

    def clear_axes(self):
        self._line_ax.clear()
        self._diff_ax.clear()

    def get_axes_xlim(self):
        return tuple(map(lambda x: x * 1E-3, self._line_ax.viewRange()[0]))


if __name__ == '__main__':
    from DatasetManager import DatasetManager, DatasetViewer
    import sys
    q_app = P61App(sys.argv)
    app = FitPlot()
    app2 = DatasetManager()
    app3 = DatasetViewer()
    app.show()
    app2.show()
    app3.show()
    sys.exit(q_app.exec_())
