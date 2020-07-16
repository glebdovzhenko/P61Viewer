from PyQt5.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg

from P61App import P61App


class MainPlot(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'w')

        graph_widget = pg.GraphicsLayoutWidget(show=True)
        self._line_ax = graph_widget.addPlot(title="Imported spectra")
        self._line_ax.setLabel('bottom', "Energy", units='eV')
        self._line_ax.setLabel('left', "Intensity", units='counts')
        self._line_ax.showGrid(x=True, y=True)
        self._lines = []

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(graph_widget)

        self.q_app.dataRowsInserted.connect(self.on_data_rows_appended)
        self.q_app.dataRowsRemoved.connect(self.on_data_rows_removed)
        self.q_app.dataActiveChanged.connect(self.on_data_active_changed)

    def on_data_rows_appended(self, pos, n_rows):
        self._lines = self._lines[:pos] + [None] * n_rows + self._lines[pos:]
        for ii in range(pos, pos + n_rows):
            data = self.q_app.data.loc[ii, ['DataX', 'DataY', 'Color']]
            self._lines[ii] = self._line_ax.plot(1E3 * data['DataX'], data['DataY'],
                                                 pen=str(hex(data['Color'])).replace('0x', '#'))

    def on_data_rows_removed(self, rows):
        for ii in sorted(rows, reverse=True):
            self._line_ax.removeItem(self._lines[ii])
            self._lines.pop(ii)

    def on_data_active_changed(self, rows):
        for ii in rows:
            if self.q_app.data.loc[ii, 'Active']:
                self._lines[ii].setPen(str(hex(self.q_app.data.loc[ii, 'Color'])).replace('0x', '#'))
            else:
                self._lines[ii].setPen(None)


if __name__ == '__main__':
    from DatasetManager import DatasetManager
    import sys
    q_app = P61App(sys.argv)
    app = MainPlot()
    app2 = DatasetManager()
    app.show()
    app2.show()
    sys.exit(q_app.exec_())
