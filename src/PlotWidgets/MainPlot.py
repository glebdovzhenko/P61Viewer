from PyQt5.QtWidgets import QTabWidget
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import logging

from P61App import P61App
from PlotWidgets.GlPlot3DWidget import GlPlot3D, GlPlot3DWidget

pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', 'w')


class MainPlot(QTabWidget):
    def __init__(self, parent=None):
        QTabWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.tab_2d = MainPlot2D(parent=self)
        self.addTab(self.tab_2d, "2D")
        self.tab_3d = MainPlot3DWidget(MainPlot3D(parent=self), parent=self)
        self.addTab(self.tab_3d, "3D")
        # self.tab_test = GlPlot3DWidget(GlPlot3D(parent=self), parent=self)
        # self.addTab(self.tab_test, " Base Class Test")


class MainPlot3DWidget(GlPlot3DWidget):
    def __init__(self, plot, parent=None):
        GlPlot3DWidget.__init__(self, plot, parent=parent)
        self.q_app = P61App.instance()

        self.q_app.dataRowsInserted.connect(self.on_data_rows_appended)
        self.q_app.dataRowsRemoved.connect(self.on_data_rows_removed)

    def autoscale(self):
        if self.q_app.data.shape[0]:
            emin = self.q_app.data['DataX'].apply(np.min).min()
            emax = self.q_app.data['DataX'].apply(np.max).max()
            imax = self.q_app.data['DataY'].apply(np.max).max()
        else:
            emin, emax, imax = None, None, None
        self._scale_to(emin, emax, imax)

    def on_data_rows_appended(self, *args, **kwargs):
        self.logger.debug('on_data_rows_appended: Handling dataRowsInserted(%s, %s)' % (str(args), str(kwargs)))
        self.plot.on_data_rows_appended(*args, **kwargs)
        if self.autoscale_cb.isChecked():
            self.autoscale()

    def on_data_rows_removed(self, *args, **kwargs):
        self.logger.debug('on_data_rows_removed: Handling dataRowsRemoved(%s, %s)' % (str(args), str(kwargs)))
        self.plot.on_data_rows_removed(*args, **kwargs)
        if self.autoscale_cb.isChecked():
            self.autoscale()


class MainPlot3D(GlPlot3D):
    def __init__(self, parent=None):
        GlPlot3D.__init__(self, parent=parent)
        self.q_app = P61App.instance()
        self._lines = []

        self.q_app.dataActiveChanged.connect(self.on_data_active_changed)
        self.q_app.dataSorted.connect(self.on_data_sorted)

    def on_data_sorted(self):
        self.logger.debug('on_data_sorted: Handling dataSorted')
        self.upd_and_redraw()

    def redraw_data(self):
        del self._lines[:]
        self.on_data_rows_appended(0, self.q_app.data.shape[0])

    def on_data_rows_appended(self, pos, n_rows):
        self._lines = self._lines[:pos] + [None] * n_rows + self._lines[pos:]

        for ii in range(pos, pos + n_rows):
            self._lines[ii] = self._init_line(ii)
            self.addItem(self._lines[ii])

        self._restack_ys()

    def on_data_rows_removed(self, rows):
        for ii in sorted(rows, reverse=True):
            self.removeItem(self._lines[ii])
            self._lines.pop(ii)

        self._restack_ys()

    def on_data_active_changed(self, rows):
        self.logger.debug('on_data_active_changed: Handling dataActiveChanged(%s)' % (str(rows),))

        for ii in rows:
            if self.q_app.data.loc[ii, 'Active']:
                self._lines[ii].setVisible(True)
            else:
                self._lines[ii].setVisible(False)

    def _init_line(self, idx):
        data = self.q_app.data.loc[idx, ['DataX', 'DataY', 'Color', 'Active']]

        pos = self.transform_xz(data['DataX'], data['DataY'])
        result = gl.GLLinePlotItem(pos=pos,
                                   color=str(hex(data['Color'])).replace('0x', '#'),
                                   antialias=True)
        result.setVisible(data['Active'])
        return result

    def _restack_ys(self):
        for ii in range(len(self._lines)):
            if self._lines[ii] is not None:
                pos = self._lines[ii].pos
                pos[:, 1] = float(ii) / float(len(self._lines)) + self.lines_origin[1]
                self._lines[ii].setData(pos=pos, antialias=True)


class MainPlot2D(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        pg.GraphicsLayoutWidget.__init__(self, parent=parent, show=True)
        self.q_app = P61App.instance()
        self.logger = logging.getLogger(str(self.__class__))

        self._line_ax = self.addPlot(title="Imported spectra")
        self._line_ax.setLabel('bottom', "Energy", units='eV')
        self._line_ax.setLabel('left', "Intensity", units='counts')
        self._line_ax.showGrid(x=True, y=True)
        self._lines = []

        self.q_app.dataRowsInserted.connect(self.on_data_rows_appended)
        self.q_app.dataRowsRemoved.connect(self.on_data_rows_removed)
        self.q_app.dataActiveChanged.connect(self.on_data_active_changed)

    def on_data_rows_appended(self, pos, n_rows):
        self.logger.debug('on_data_rows_appended: Handling dataRowsInserted(%d, %d)' % (pos, n_rows))
        self._lines = self._lines[:pos] + [None] * n_rows + self._lines[pos:]
        for ii in range(pos, pos + n_rows):
            data = self.q_app.data.loc[ii, ['DataX', 'DataY', 'Color']]
            self._lines[ii] = self._line_ax.plot(1E3 * data['DataX'], data['DataY'],
                                                 pen=str(hex(data['Color'])).replace('0x', '#'))

    def on_data_rows_removed(self, rows):
        self.logger.debug('on_data_rows_removed: Handling dataRowsInserted(%s)' % (str(rows), ))
        for ii in sorted(rows, reverse=True):
            self._line_ax.removeItem(self._lines[ii])
            self._lines.pop(ii)

    def on_data_active_changed(self, rows):
        self.logger.debug('on_data_active_changed: Handling dataActiveChanged(%s)' % (str(rows),))
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
