"""
src/P61ViewerMain.py
====================
.. _QApplication: https://doc.qt.io/qtforpython/PySide2/QtWidgets/QApplication.html
.. _QMainWindow: https://doc.qt.io/qtforpython/PySide2/QtWidgets/QMainWindow.html

Executable script for the application.

Launches the P61App (QApplication_ child class) and a P61Viewer (QMainWindow_ child class) instance.
"""
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QTabWidget
import sys
from PlotWidgets import MainPlotWidget, FitPlotWidget
from ListWidgets import EditableListWidget
from FitWidgets import FitWidget
from P61App import P61App


class P61Viewer(QMainWindow):
    """
    QMainWindow child
    """
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent=parent)

        # initiate self
        self.resize(1200, 800)
        self.setWindowTitle('P61 Spectrum Viewer')

        # initiate widgets
        self.cw = QTabWidget(parent=self)
        self.setCentralWidget(self.cw)
        view_tab = QWidget()

        self.file_w = EditableListWidget(parent=self)
        self.fit_w = FitWidget(parent=self)
        self.view_plot_w = MainPlotWidget(parent=self)
        self.fit_plot_w = FitPlotWidget(parent=self)

        # set up layouts
        view_layout = QHBoxLayout()
        view_tab.setLayout(view_layout)
        view_layout.addWidget(self.view_plot_w, 3)
        view_layout.addWidget(self.file_w, 1)

        fit_tab = QWidget()
        fit_layout = QHBoxLayout()
        fit_tab.setLayout(fit_layout)
        fit_layout.addWidget(self.fit_w, 1)
        fit_layout.addWidget(self.fit_plot_w, 3)

        self.cw.addTab(view_tab, 'View')
        self.cw.addTab(fit_tab, 'Fit')


if __name__ == '__main__':
    q_app = P61App(sys.argv)
    app = P61Viewer()
    app.show()
    sys.exit(q_app.exec_())
