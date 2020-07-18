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

    def on_data_rows_appended(self, *args, **kwargs):
        self.plot.on_data_rows_appended(*args, **kwargs)
        if self.autoscale_cb.isChecked():
            self.autoscale()

    def on_data_rows_removed(self, *args, **kwargs):
        self.plot.on_data_rows_removed(*args, **kwargs)
        if self.autoscale_cb.isChecked():
            self.autoscale()

    def on_data_active_changed(self, *args, **kwargs):
        self.plot.on_data_active_changed(*args, **kwargs)
        if self.autoscale_cb.isChecked():
            self.autoscale()


class PTPlot3D(GlPlot3D):
    def __init__(self, parent=None):
        GlPlot3D.__init__(self, parent=parent)
        self.q_app = P61App.instance()

    def on_data_rows_appended(self, pos, n_rows):
        for ii in range(self.q_app.data.shape[0]):
            if self.q_app.data.loc[ii, 'Active']:
                self._lines.append(self._init_line(ii))
                self.addItem(self._lines[-1])

        self._restack_ys()

    def on_data_rows_removed(self, rows):
        self.upd_and_redraw()
        self._restack_ys()

    def on_data_active_changed(self, rows):
        self.upd_and_redraw()
        self._restack_ys()


if __name__ == '__main__':
    from DatasetManager import DatasetManager
    import sys
    q_app = P61App(sys.argv)
    app = PTPlot3DWidget()
    app2 = DatasetManager()
    app.show()
    app2.show()
    sys.exit(q_app.exec_())
