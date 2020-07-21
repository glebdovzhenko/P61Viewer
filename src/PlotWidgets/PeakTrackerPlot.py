from PyQt5.Qt import QVector3D
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import pandas as pd
from itertools import chain

from P61App import P61App
from PlotWidgets.GlPlot3DWidget import GlPlot3D, GlPlot3DWidget

pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', 'w')


class PTPlot3DWidget(GlPlot3DWidget):
    def __init__(self, plot, parent=None):
        self.plot_2d = PTPlot2D()
        GlPlot3DWidget.__init__(self, plot, parent=parent)
        self.q_app = P61App.instance()

        self.layout().addWidget(self.plot_2d, 4, 1, 1, 7)
        self.layout().setRowStretch(4, 2)

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
        if self.plot_2d is not None:
            self.plot_2d.set_axes_lim(1E3 * self.plot.emin, 1E3 * self.plot.emax, self.plot.imax)


class PTPlot3D(GlPlot3D):
    cam_default = {'pos': QVector3D(0.5 * GlPlot3D.x_ratio, 0.5, 0.4), 'distance': 3, 'azimuth': -90, 'elevation': 20}

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

        # if data[1] is not None:
        #     print(idx, '::', ', '.join(str(l) + ':' + str(r) for l, r in zip(data[1]['left_bases'], data[1]['right_bases'])))

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


class PTPlot2D(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        pg.GraphicsLayoutWidget.__init__(self, parent=parent, show=True)
        self.q_app = P61App.instance()

        self._peak_hist = None

        self._line_ax = self.addPlot(title="Fit")
        self._line_ax.setLabel('bottom', "Energy", units='eV')
        self._line_ax.setLabel('left', "Intensity", units='counts')
        self._line_ax.showGrid(x=True, y=True)

        self.q_app.selectedIndexChanged.connect(self.on_selected_active_changed)
        self.q_app.peakListChanged.connect(self.on_peak_list_changed)

    def on_peak_list_changed(self):
        data = self.q_app.data['PeakList']
        data = data.apply(lambda x: None if x is None else x[0][0])
        data = data[pd.notnull(data)]
        data = list(chain.from_iterable(data))

        xx = self.q_app.data.loc[self.q_app.get_selected_idx(), 'DataX']
        yy, xx = np.histogram(data, bins=np.linspace(np.min(xx), np.max(xx), min(5000, xx.shape[0])))
        self._peak_hist = (1E3 * xx, yy)
        self.on_selected_active_changed(self.q_app.get_selected_idx())

    def on_selected_active_changed(self, idx):
        self.clear_axes()
        if idx != -1:
            data = self.q_app.data.loc[idx, ['DataX', 'DataY', 'Color', 'GeneralFitResult']]

            self._line_ax.plot(1E3 * data['DataX'], data['DataY'],
                               pen=pg.mkPen(color='#000000'))
            if self._peak_hist is not None:
                self._line_ax.plot(*self._peak_hist, stepMode=True, fillLevel=0, fillOutline=True,
                                   brush=(255, 0, 0, 255))

    def clear_axes(self):
        self._line_ax.clear()

    def get_axes_xlim(self):
        return tuple(map(lambda x: x * 1E-3, self._line_ax.viewRange()[0]))

    def set_axes_lim(self, xmin, xmax, ymax):
        if xmin is not None and xmax is not None:
            self._line_ax.setXRange(xmin, xmax)
        if ymax is not None:
            self._line_ax.setYRange(0, ymax)


if __name__ == '__main__':
    from DatasetManager import DatasetManager
    import sys
    q_app = P61App(sys.argv)
    app = PTPlot3DWidget()
    app2 = DatasetManager()
    app.show()
    app2.show()
    sys.exit(q_app.exec_())
