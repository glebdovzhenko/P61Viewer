from PyQt5.QtWidgets import QTabWidget, QWidget, QGridLayout, QLabel, QCheckBox
from PyQt5.Qt import QVector3D
from PyQt5 import QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

from P61App import P61App
from PlotWidgets.GlPlot3DWidget import GlPlot3D, GlPlot3DWidget

pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', 'w')


class PTPlot3DWidget(GlPlot3DWidget):
    def __init__(self, plot, parent=None):
        GlPlot3DWidget.__init__(self, plot, parent=parent)
        self.q_app = P61App.instance()

        self.q_app.dataRowsInserted.connect(self.on_data_rows_appended)
        self.q_app.dataRowsRemoved.connect(self.on_data_rows_removed)
        self.q_app.dataActiveChanged.connect(self.on_data_active_changed)
        self.q_app.peakListChanged.connect(self.on_peak_list_changed)

    def autoscale(self):
        if len(self.q_app.get_active_ids()) > 0:
            emin = self.q_app.data.loc[self.q_app.get_active_ids(), 'DataX'].apply(np.min).min()
            emax = self.q_app.data.loc[self.q_app.get_active_ids(), 'DataX'].apply(np.max).max()
            imax = self.q_app.data.loc[self.q_app.get_active_ids(), 'DataY'].apply(np.max).max()
        else:
            emin, emax, imax = None, None, None
        self._scale_to(emin, emax, imax)

    def on_data_rows_appended(self, *args, **kwargs):
        self.plot.upd_and_redraw()
        if self.autoscale_cb.isChecked():
            self.autoscale()

    def on_data_rows_removed(self, *args, **kwargs):
        self.plot.upd_and_redraw()
        if self.autoscale_cb.isChecked():
            self.autoscale()

    def on_data_active_changed(self, *args, **kwargs):
        self.plot.upd_and_redraw()
        if self.autoscale_cb.isChecked():
            self.autoscale()

    def on_peak_list_changed(self, *args, **kwargs):
        self.plot.upd_and_redraw()

    def _update_scale(self, *args, **kwargs):
        GlPlot3DWidget._update_scale(self, *args, **kwargs)
        self.q_app.peak_search_range = (self.plot.emin, self.plot.emax)


class PTPlot3D(GlPlot3D):
    def __init__(self, parent=None):
        GlPlot3D.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self._lines = []
        self._peak_scatters = []

    def redraw_data(self):
        del self._lines[:]
        del self._peak_scatters[:]

        for idx in self.q_app.get_active_ids():
            self._lines.append(self._init_line(idx))
            self.addItem(self._lines[-1])
            self._peak_scatters.append(self._init_peak_scatter(idx))
            if self._peak_scatters[-1] is not None:
                self.addItem(self._peak_scatters[-1])

        self._restack_ys()

    def _init_line(self, idx):
        data = self.q_app.data.loc[idx, ['DataX', 'DataY']]
        pos = self.transform_xz(data['DataX'], data['DataY'])
        result = gl.GLLinePlotItem(pos=pos, color='#ffffff', antialias=True)
        return result

    def _init_peak_scatter(self, idx):
        data = self.q_app.data.loc[idx, 'PeakList']
        if data is None:
            return None

        peak_xs = data[0][0]
        peak_ys = data[0][1]

        if data[1] is not None:
            print(idx, '::', ', '.join(str(l) + ':' + str(r) for l, r in zip(data[1]['left_bases'], data[1]['right_bases'])))

        pos = self.transform_xz(peak_xs, peak_ys)
        result = gl.GLScatterPlotItem(pos=pos, color=(1, 0, 0, 1))
        return result

    def _restack_ys(self):
        for ii in range(len(self._lines)):
            if self._lines[ii] is not None:
                pos = self._lines[ii].pos
                pos[:, 1] = float(ii) / float(len(self._lines)) + self.lines_origin[1]
                self._lines[ii].setData(pos=pos, antialias=True)
            if self._peak_scatters[ii] is not None:
                pos = self._peak_scatters[ii].pos
                pos[:, 1] = float(ii) / float(len(self._lines)) + self.lines_origin[1]
                self._peak_scatters[ii].setData(pos=pos)


if __name__ == '__main__':
    from DatasetManager import DatasetManager
    import sys
    q_app = P61App(sys.argv)
    app = PTPlot3DWidget()
    app2 = DatasetManager()
    app.show()
    app2.show()
    sys.exit(q_app.exec_())
