"""
src/P61ViewerMain.py
====================
.. _QApplication: https://doc.qt.io/qtforpython/PySide2/QtWidgets/QApplication.html
.. _QMainWindow: https://doc.qt.io/qtforpython/PySide2/QtWidgets/QMainWindow.html

This python file serves as the executable script for the application.

Launches the :code:`P61App` (QApplication_ child class) and a :code:`P61Viewer` (QMainWindow_ child class) instances.
"""
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QTabWidget, QSystemTrayIcon
from PyQt5.QtGui import QIcon
import sys
from PlotWidgets import MainPlot
from DatasetManager import DatasetManager
from FitWidgets import GeneralFitWidget
from PeakAnalysisWidgets import PeakAnalysisWidget

from P61App import P61App


class P61Viewer(QMainWindow):
    """
    Main window class for the application. Collects all widgets in the same layout and instantiates them.

    List of widgets:

    - :code:`EditableListWidget` List on the right of the 'View' tab. Allows to add, remove, activate (show on the
      plot and use for fit) and deactivate (stop showing on the plot and using for fit) datasets. All operations can be
      done in groups using multiple selection;
    - :code:`MainPlotWidget` shows all active datasets from the :code:`EditableListWidget`;
    - :code:`FitWidget` shows the model builder, fit parameters, list of datasets to fit and controls;
    - :code:`FitPlotWidget`: plots the fitted data together with the model function and its parts and a difference
      plot;
    """
    def __init__(self, parent=None):
        """
        Initiates all widgets and defines the main window layout.
        :param parent:
        """
        QMainWindow.__init__(self, parent=parent)

        # initiate self
        self.resize(1200, 800)
        self.setWindowTitle(P61App.name + ' ' + P61App.version)

        # initiate widgets
        self.cw = QTabWidget(parent=self)
        self.setCentralWidget(self.cw)
        self.view_tab = QWidget()

        self.file_w = DatasetManager(parent=self)
        self.fit_w = GeneralFitWidget(parent=self)
        self.view_plot_w = MainPlot(parent=self)
        self.pa_w = PeakAnalysisWidget(parent=self)

        # set up layouts
        view_layout = QHBoxLayout()
        self.view_tab.setLayout(view_layout)
        view_layout.addWidget(self.view_plot_w, 3)
        view_layout.addWidget(self.file_w, 1)

        self.fit_tab = QWidget()
        fit_layout = QHBoxLayout()
        self.fit_tab.setLayout(fit_layout)
        fit_layout.addWidget(self.fit_w)

        self.cw.addTab(self.view_tab, 'Import and view')
        self.cw.addTab(self.fit_tab, 'Arbitrary function fit')
        self.cw.addTab(self.pa_w, 'Peak analysis')


if __name__ == '__main__':
    q_app = P61App(sys.argv)

    trayIcon = QSystemTrayIcon(QIcon("../img/icon.png"), q_app)
    trayIcon.show()

    app = P61Viewer()
    app.show()
    sys.exit(q_app.exec_())
