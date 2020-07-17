from PyQt5.QtWidgets import QTabWidget, QWidget, QGridLayout, QLabel
from PyQt5.Qt import QVector3D
from PyQt5 import QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

from P61App import P61App

pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', 'w')


class MainPlot(QTabWidget):
    def __init__(self, parent=None):
        QTabWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.tab_2d = MainPlot2D(parent=self)
        self.addTab(self.tab_2d, "2D lines")
        self.tab_3d = MainPlot3DWidget(parent=self)
        self.addTab(self.tab_3d, "3D lines")


class MainPlot3DWidget(QWidget):
    def __init__(self, parent=None):
        from FitWidgets import FloatEdit

        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.plot = MainPlot3D(parent=self)
        self.zscale_label = QLabel('Intensity scale')
        self.zscale_edit = FloatEdit(init_val=1E3)
        self.erange_label = QLabel('Energy range (keV)')
        self.erange_min = FloatEdit(init_val=700)
        self.erange_max = FloatEdit(init_val=1200)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.plot, 1, 1, 1, 5)
        layout.addWidget(self.zscale_label, 2, 1, 1, 1)
        layout.addWidget(self.zscale_edit, 2, 2, 1, 1)
        layout.addWidget(self.erange_label, 2, 3, 1, 1)
        layout.addWidget(self.erange_min, 2, 4, 1, 1)
        layout.addWidget(self.erange_max, 2, 5, 1, 1)

        self.zscale_edit.valueChanged.connect(self.update_plot)
        self.erange_min.valueChanged.connect(self.update_plot)
        self.erange_max.valueChanged.connect(self.update_plot)

    def update_plot(self, *args, **kwargs):
        self.plot.update_scale(self.erange_min.value, self.erange_max.value, self.zscale_edit.value)


class MainPlot3D(gl.GLViewWidget):
    def __init__(self, parent=None):
        gl.GLViewWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self._lines = []
        self.e_range = (700, 1200)
        self.z_scale = 1E3
        self.setCameraPosition(pos=QVector3D(0.5, 0.5, 0.0), distance=1.5, azimuth=-90, elevation=20)

        self.q_app.dataRowsInserted.connect(self.on_data_rows_appended)
        self.q_app.dataRowsRemoved.connect(self.on_data_rows_removed)
        self.q_app.dataActiveChanged.connect(self.on_data_active_changed)

    def update_scale(self, erange_min, erange_max, zscale):
        self.e_range = erange_min, erange_max
        self.z_scale = zscale

        for item in self.items:
            item._setView(None)
        self.items = []
        self.update()
        del self._lines[:]

        self.on_data_rows_appended(0, self.q_app.data.shape[0])

    def keyPressEvent(self, ev):
        dx, dy, dz, dr = 0., 0., 0., 0.
        if ev.key() == QtCore.Qt.Key_W:
            dy = 0.1
        elif ev.key() == QtCore.Qt.Key_S:
            dy = -0.1
        elif ev.key() == QtCore.Qt.Key_A:
            dx = -0.1
        elif ev.key() == QtCore.Qt.Key_D:
            dx = +0.1
        elif ev.key() == QtCore.Qt.Key_R:
            dz = 0.1
        elif ev.key() == QtCore.Qt.Key_F:
            dz = -0.1
        elif ev.key() == QtCore.Qt.Key_Z:
            dr = -0.1
        elif ev.key() == QtCore.Qt.Key_X:
            dr = 0.1

        self.setCameraPosition(distance=self.opts['distance'] + dr)
        for line in self._lines:
            line.translate(dx, dy, dz)

        gl.GLViewWidget.keyPressEvent(self, ev)

    def on_data_rows_appended(self, pos, n_rows):
        self._lines = self._lines[:pos] + [None] * n_rows + self._lines[pos:]
        for ii in range(pos, pos + n_rows):
            data = self.q_app.data.loc[ii, ['DataX', 'DataY', 'Color', 'Active']]
            xx = np.array(1E3 * data['DataX'])
            zz = np.array(data['DataY'])
            yy = np.array([ii] * zz.shape[0], dtype=np.float)

            yy = yy[(xx < self.e_range[1] * 1E3) & (xx > self.e_range[0] * 1E3)]
            zz = zz[(xx < self.e_range[1] * 1E3) & (xx > self.e_range[0] * 1E3)]
            xx = xx[(xx < self.e_range[1] * 1E3) & (xx > self.e_range[0] * 1E3)]

            xx = (xx - self.e_range[0] * 1E3) / (self.e_range[1] * 1E3 - self.e_range[0] * 1E3)
            zz /= self.z_scale
            yy /= np.float(len(self._lines))

            pts = np.vstack([xx, yy, zz]).transpose()
            self._lines[ii] = gl.GLLinePlotItem(pos=pts, color=str(hex(data['Color'])).replace('0x', '#'),
                                                antialias=True)
            if not data['Active']:
                self._lines[ii].setVisible(False)
            self.addItem(self._lines[ii])

    def on_data_rows_removed(self, rows):
        for ii in sorted(rows, reverse=True):
            self.removeItem(self._lines[ii])
            self._lines.pop(ii)

    def on_data_active_changed(self, rows):
        for ii in rows:
            if self.q_app.data.loc[ii, 'Active']:
                self._lines[ii].setVisible(True)
            else:
                self._lines[ii].setVisible(False)


class MainPlot2D(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        pg.GraphicsLayoutWidget.__init__(self, parent=parent, show=True)
        self.q_app = P61App.instance()

        self._line_ax = self.addPlot(title="Imported spectra")
        self._line_ax.setLabel('bottom', "Energy", units='eV')
        self._line_ax.setLabel('left', "Intensity", units='counts')
        self._line_ax.showGrid(x=True, y=True)
        self._lines = []

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
