from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox
from PyQt5.Qt import QVector3D
from PyQt5 import QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

from P61App import P61App

pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', 'w')


class GlPlot3DWidget(QWidget):
    def __init__(self, plot, parent=None):
        from FitWidgets import FloatEdit

        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.explanation_label = QLabel('[W] [A] [S] [D] move the plot in XY plane, [R] [F] move it along Z axis. '
                                        'Arrow keys or mouse click & drag rotate the camera. '
                                        '[Z] and [X] zoom the camera in and out. ')
        self.explanation_label.setMaximumHeight(20)
        self.zscale_label = QLabel('Intensity scale')
        self.zscale_edit = FloatEdit(init_val=1E3)
        self.erange_label = QLabel('Energy range (keV)')
        self.erange_min = FloatEdit(init_val=0)
        self.erange_max = FloatEdit(init_val=200)
        self.plot = plot
        self.autoscale_cb = QCheckBox(text='Autoscale')
        self.autoscale_cb.setChecked(True)
        self.erange_min.setReadOnly(True)
        self.erange_max.setReadOnly(True)
        self.zscale_edit.setReadOnly(True)
        self.update_plot()

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.explanation_label, 1, 1, 1, 6)
        layout.addWidget(self.plot, 2, 1, 1, 6)
        layout.addWidget(self.autoscale_cb, 3, 1, 1, 1)
        layout.addWidget(self.zscale_label, 3, 2, 1, 1)
        layout.addWidget(self.zscale_edit, 3, 3, 1, 1)
        layout.addWidget(self.erange_label, 3, 4, 1, 1)
        layout.addWidget(self.erange_min, 3, 5, 1, 1)
        layout.addWidget(self.erange_max, 3, 6, 1, 1)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 5)
        layout.setRowStretch(3, 1)

        self.zscale_edit.valueChanged.connect(self.update_plot)
        self.erange_min.valueChanged.connect(self.update_plot)
        self.erange_max.valueChanged.connect(self.update_plot)
        self.autoscale_cb.stateChanged.connect(self.on_autoscale_sc)

    def on_autoscale_sc(self, state):
        for edit in (self.erange_min, self.erange_max, self.zscale_edit):
            edit.setReadOnly(bool(state))
        if state:
            self.autoscale()

    def update_plot(self, *args, **kwargs):
        self.plot.e_range = (self.erange_min.get_value(), self.erange_max.get_value())
        self.plot.z_scale = self.zscale_edit.get_value()
        self.plot.upd_and_redraw()

    def autoscale(self):
        if self.q_app.data.shape[0]:
            self.erange_min.set_value(self.q_app.data['DataX'].apply(np.min).min(), emit=False)
            self.erange_max.set_value(self.q_app.data['DataX'].apply(np.max).max(), emit=False)
            self.zscale_edit.value = self.q_app.data['DataY'].apply(np.max).max()
        else:
            self.erange_min.set_value(0, emit=False)
            self.erange_max.set_value(200, emit=False)
            self.zscale_edit.value = 1E3


class GlPlot3D(gl.GLViewWidget):
    def __init__(self, parent=None):
        gl.GLViewWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.lines_origin = [0., 0., 0.]
        self._lines = []
        self.e_range = None
        self.z_scale = None
        self.setCameraPosition(pos=QVector3D(0.5, 0.5, 0.0), distance=1.5, azimuth=-90, elevation=20)

        self.grid_xy = gl.GLGridItem()
        self.grid_yz = gl.GLGridItem()
        self.grid_xz = gl.GLGridItem()
        self.text_objs = []
        self.x_ticks = 7
        self.z_ticks = 2
        self._init_axes()

    def update_text_objs(self):
        if self.e_range is not None:
            for ii, ee in enumerate(np.linspace(self.e_range[0], self.e_range[1], self.x_ticks)):
                self.text_objs[ii][3] = '%.0f' % ee
        else:
            for ii in range(self.x_ticks):
                self.text_objs[ii][3] = ''

        if self.z_scale is not None:
            for ii, zz in enumerate(np.linspace(0, self.z_scale, self.z_ticks)):
                self.text_objs[ii + self.x_ticks][3] = '%.0f' % zz
        else:
            for ii in range(self.z_ticks):
                self.text_objs[ii + self.x_ticks][3] = ''

    def upd_and_redraw(self):
        for item in self.items:
            item._setView(None)
        self.items = []
        self.update()
        del self._lines[:]

        self.addItem(self.grid_xy)
        self.addItem(self.grid_yz)
        self.addItem(self.grid_xz)

        self.update_text_objs()

        self.on_data_rows_appended(0, self.q_app.data.shape[0])

    def on_data_rows_appended(self, *args, **kwargs):
        pass

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

        for item in self.items:
            item.translate(dx, dy, dz)

        for to in self.text_objs:
            to[0] += dx
            to[1] += dy
            to[2] += dz

        self.lines_origin[0] += dx
        self.lines_origin[1] += dy
        self.lines_origin[2] += dz

        gl.GLViewWidget.keyPressEvent(self, ev)

    def _prepare_line_data(self, idx):
        data = self.q_app.data.loc[idx, ['DataX', 'DataY', 'Color', 'Active']]

        xx = np.array(1E3 * data['DataX'], dtype=np.float)
        zz = np.array(data['DataY'], dtype=np.float)
        yy = np.array([idx] * zz.shape[0], dtype=np.float)

        yy = yy[(xx < self.e_range[1] * 1E3) & (xx > self.e_range[0] * 1E3)]
        zz = zz[(xx < self.e_range[1] * 1E3) & (xx > self.e_range[0] * 1E3)]
        xx = xx[(xx < self.e_range[1] * 1E3) & (xx > self.e_range[0] * 1E3)]

        xx = (xx - self.e_range[0] * 1E3) / (self.e_range[1] * 1E3 - self.e_range[0] * 1E3)
        zz /= self.z_scale
        yy /= np.float(len(self._lines))

        xx += self.lines_origin[0]
        yy += self.lines_origin[1]
        zz += self.lines_origin[2]

        return np.vstack([xx, yy, zz]).transpose()

    def _init_line(self, idx):
        data = self.q_app.data.loc[idx, ['Color', 'Active']]
        result = gl.GLLinePlotItem(pos=self._prepare_line_data(idx),
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

    def _init_axes(self):
        self.grid_xy.scale(.05, .05, 1)
        self.grid_xy.translate(.5, .5, 0)
        self.grid_xy.setDepthValue(10)

        self.grid_yz.scale(.05, .05, 1)
        self.grid_yz.rotate(90, 0, 1, 0)
        self.grid_yz.translate(0., 0.5, 0.5)
        self.grid_yz.setDepthValue(10)

        self.grid_xz.scale(.05, .05, 1)
        self.grid_xz.rotate(90, 1, 0, 0)
        self.grid_xz.translate(0.5, 1.0, 0.5)
        self.grid_xz.setDepthValue(10)

        for xx in np.linspace(0., 1., self.x_ticks):
            self.text_objs.append([xx, 0., -0.05, ''])

        for zz in np.linspace(0., 1., self.z_ticks):
            self.text_objs.append([0., -0.05, zz, ''])

        self.text_objs.append([0.5, 0., -0.1, 'keV'])

    def paintGL(self, *args, **kwds):
        gl.GLViewWidget.paintGL(self, *args, **kwds)

        self.qglColor(QtCore.Qt.white)
        for to in self.text_objs:
            self.renderText(*to)


if __name__ == '__main__':
    from DatasetManager import DatasetManager
    import sys
    q_app = P61App(sys.argv)
    app = GlPlot3DWidget()
    app2 = DatasetManager()
    app.show()
    app2.show()
    sys.exit(q_app.exec_())
