from PyQt5.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from P61App import P61App


class PAHeatMapWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        map_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self._line_ax = map_canvas.figure.subplots()
        self._line_ax.set_xlabel('Energy, [keV]')
        self._line_ax.set_ylabel('Spectrum #')

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(map_canvas)
        layout.addWidget(NavigationToolbar(map_canvas, self))

        self.q_app.dataRowsAppended.connect(self.on_data_rows_appended)
        self.q_app.dataRowsRemoved.connect(self.on_data_rows_removed)
        self.q_app.dataActiveChanged.connect(self.on_data_active_changed)

    def on_data_rows_appended(self, n_rows):
        for ii in range(self.q_app.data.shape[0] - n_rows, self.q_app.data.shape[0]):
            data = self.q_app.data.loc[ii, ['DataX', 'DataY', 'Color']]
            self._line_ax.plot(data['DataX'], data['DataY'], color=str(hex(data['Color'])).replace('0x', '#'))
        self.update_line_axes()

    def on_data_rows_removed(self, rows):
        for ii in sorted(rows, reverse=True):
            self._line_ax.lines[ii].remove()
        self.update_line_axes(autoscale=False)

    def on_data_active_changed(self, rows):
        for ii in rows:
            if self.q_app.data.loc[ii, 'Active']:
                self._line_ax.lines[ii].set_linestyle('-')
            else:
                self._line_ax.lines[ii].set_linestyle('')
        self.update_line_axes(autoscale=False)

    def update_line_axes(self, autoscale=True):
        if autoscale:
            self._line_ax.autoscale()
            self._line_ax.figure.canvas.toolbar.update()
        self._line_ax.figure.canvas.draw()

    def update_data(self):
        data = self.q_app.data.loc[:, ['DataX', 'DataY']]


if __name__ == '__main__':
    from ListWidgets import EditableListWidget
    import sys
    q_app = P61App(sys.argv)
    app = PAHeatMapWidget()
    app2 = EditableListWidget()
    app.show()
    app2.show()
    sys.exit(q_app.exec_())
