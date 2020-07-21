from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QPushButton
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

        self.plot = plot
        self.explanation_label = QLabel('[W] [A] [S] [D] move the plot in XY plane, [R] [F] move it along Z axis. '
                                        'Arrow keys or mouse click & drag rotate the camera. '
                                        '[Z] and [X] zoom the camera in and out. ')
        self.explanation_label.setMaximumHeight(20)
        self.zscale_label = QLabel('Intensity scale')
        self.imax_edit = FloatEdit(init_val=self.plot.imax_default)
        self.erange_label = QLabel('Energy range (keV)')
        self.emin_edit = FloatEdit(init_val=self.plot.emin_default)
        self.emax_edit = FloatEdit(init_val=self.plot.emax_default)
        self.autoscale_cb = QCheckBox(text='Autoscale')
        self.autoscale_cb.setChecked(True)
        self.emin_edit.setReadOnly(True)
        self.emax_edit.setReadOnly(True)
        self.imax_edit.setReadOnly(True)
        self._update_scale()
        self.view_to_default = QPushButton(u'👀')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.explanation_label, 1, 1, 1, 7)
        layout.addWidget(self.plot, 2, 1, 1, 7)
        layout.addWidget(self.view_to_default, 3, 1, 1, 1)
        layout.addWidget(self.autoscale_cb, 3, 2, 1, 1)
        layout.addWidget(self.zscale_label, 3, 3, 1, 1)
        layout.addWidget(self.imax_edit, 3, 4, 1, 1)
        layout.addWidget(self.erange_label, 3, 5, 1, 1)
        layout.addWidget(self.emin_edit, 3, 6, 1, 1)
        layout.addWidget(self.emax_edit, 3, 7, 1, 1)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 5)
        layout.setRowStretch(3, 1)

        self.imax_edit.valueChanged.connect(self._update_scale)
        self.emin_edit.valueChanged.connect(self._update_scale)
        self.emax_edit.valueChanged.connect(self._update_scale)
        self.autoscale_cb.stateChanged.connect(self._on_autoscale_sc)
        self.view_to_default.clicked.connect(self.set_view_to_default)

    def set_view_to_default(self):
        self.plot.translate_scene(-self.plot.lines_origin[0], -self.plot.lines_origin[1], -self.plot.lines_origin[2])
        self.plot.setCameraPosition(**self.plot.cam_default)

    def autoscale(self):
        """
        Function to be overridden in subclasses to change default autoscaling behaviour,
        which is scale to default values
        :return:
        """
        self._scale_to()

    def _on_autoscale_sc(self, state):
        for edit in (self.emin_edit, self.emax_edit, self.imax_edit):
            edit.setReadOnly(bool(state))
        if state:
            self.autoscale()

    def _update_scale(self, *args, **kwargs):
        self.plot.emin = self.emin_edit.get_value()
        self.plot.emax = self.emax_edit.get_value()
        self.plot.imax = self.imax_edit.get_value()
        self.plot.upd_and_redraw()

    def _scale_to(self, e_min=None, e_max=None, z_max=None):
        if e_min is not None:
            self.emin_edit.set_value(e_min, emit=False)
        else:
            self.emin_edit.set_value(self.plot.emin_default, emit=False)

        if e_max is not None:
            self.emax_edit.set_value(e_max, emit=False)
        else:
            self.emax_edit.set_value(self.plot.emax_default, emit=False)

        if z_max is not None:
            self.imax_edit.set_value(z_max, emit=True)
        else:
            self.imax_edit.set_value(self.plot.imax_default, emit=True)


class GlPlot3D(gl.GLViewWidget):
    emin_default = 0
    emax_default = 200
    imax_default = 1E3  # default values for shown energy and intensity range (min intensity is always 0)
    x_ratio = 16. / 9.  # shows how much longer the x axis is on the plot compared to y and z
    cam_default = {'pos': QVector3D(0.5 * x_ratio, 0.5, 0.5), 'distance': 2.5, 'azimuth': -90, 'elevation': 20}

    def __init__(self, parent=None):
        gl.GLViewWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.lines_origin = [0., 0., 0.]
        self.emin = self.emin_default
        self.emax = self.emax_default
        self.imax = self.imax_default
        self.setCameraPosition(**self.cam_default)

        self.grid_xy = gl.GLGridItem(size=QVector3D(20. * self.x_ratio, 20., 1.))
        self.grid_yz = gl.GLGridItem()
        self.grid_xz = gl.GLGridItem(size=QVector3D(20. * self.x_ratio, 20., 1.))
        self.text_objs = []
        self.x_ticks = 7
        self.z_ticks = 2
        self._init_axes()

    def redraw_data(self):
        """
        Function that generates lines and adds them to the plot.
        Base class behaviour is to do nothing.

        :return:
        """
        pass

    def _update_text_objs(self):
        for ii, ee in enumerate(np.linspace(self.emin, self.emax, self.x_ticks)):
            self.text_objs[ii][3] = '%.0f' % ee

        for ii, zz in enumerate(np.linspace(0, self.imax, self.z_ticks)):
            self.text_objs[ii + self.x_ticks][3] = '%.0f' % zz

    def upd_and_redraw(self):
        # clear the scene
        for item in self.items:
            item._setView(None)
        self.items = []
        self.update()

        # draw the axes
        self.addItem(self.grid_xy)
        self.addItem(self.grid_yz)
        self.addItem(self.grid_xz)
        self._update_text_objs()

        # delete old and create + draw new lines
        self.redraw_data()

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
        self.translate_scene(dx, dy, dz)

        gl.GLViewWidget.keyPressEvent(self, ev)

    def translate_scene(self, dx, dy, dz):
        for item in self.items:
            item.translate(dx, dy, dz)

        for to in self.text_objs:
            to[0] += dx
            to[1] += dy
            to[2] += dz

        self.lines_origin[0] += dx
        self.lines_origin[1] += dy
        self.lines_origin[2] += dz

    def transform_xz(self, energy, intensity):
        """
        Turns energy and intensity vestors as stored in P61App.data to stacked XYZ values to plot on the 3D plot.
        Fills the Y values with 0s (relative to the plot axes origin), because after new lines are added / removed
        a restacking of Y axis is needed for every line anyway to put all lines at the equal distance from one another
        and restacking behaviour is subclass-specific.

        :param energy:
        :param intensity:
        :param index:
        :return:
        """
        xx = np.array(1E3 * energy, dtype=np.float)
        zz = np.array(intensity, dtype=np.float)
        yy = np.array([0.0] * zz.shape[0], dtype=np.float)

        yy = yy[(xx < self.emax * 1E3) & (xx > self.emin * 1E3)]
        zz = zz[(xx < self.emax * 1E3) & (xx > self.emin * 1E3)]
        xx = xx[(xx < self.emax * 1E3) & (xx > self.emin * 1E3)]

        xx = self.x_ratio * (xx - self.emin * 1E3) / (self.emax * 1E3 - self.emin * 1E3)
        zz /= self.imax

        xx += self.lines_origin[0]
        yy += self.lines_origin[1]
        zz += self.lines_origin[2]

        return np.vstack([xx, yy, zz]).transpose()

    def _init_axes(self):
        self.grid_xy.scale(.05, .05, 1)
        self.grid_xy.translate(.5 * self.x_ratio, .5, 0)
        self.grid_xy.setDepthValue(10)

        self.grid_yz.scale(.05, .05, 1)
        self.grid_yz.rotate(90, 0, 1, 0)
        self.grid_yz.translate(0., 0.5, 0.5)
        self.grid_yz.setDepthValue(10)

        self.grid_xz.scale(.05, .05, 1)
        self.grid_xz.rotate(90, 1, 0, 0)
        self.grid_xz.translate(.5 * self.x_ratio, 1.0, 0.5)
        self.grid_xz.setDepthValue(10)

        for xx in np.linspace(0., self.x_ratio, self.x_ticks):
            self.text_objs.append([xx, 0., -0.05, ''])

        for zz in np.linspace(0., 1., self.z_ticks):
            self.text_objs.append([0., -0.05, zz, ''])

        self.text_objs.append([.5 * self.x_ratio, 0., -0.1, 'keV'])

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
