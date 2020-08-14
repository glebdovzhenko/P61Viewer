from PyQt5.QtWidgets import QWidget, QGridLayout, QTabWidget

from P61App import P61App

from PeakTrackerWidgets.AutoFind import AutoFindWidget
from PeakTrackerWidgets.PeakFit import PeakFitWidget
from DatasetManager import DatasetViewer
from PlotWidgets import PTPlot3D, PTPlot3DWidget


class PeakAnalysisWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.tabs = QTabWidget(parent=self)
        self.afw = AutoFindWidget(parent=self)
        self.fit = PeakFitWidget(parent=self)
        self.tabs.addTab(self.afw, 'Search')
        self.tabs.addTab(self.fit, 'Fit')
        self.list = DatasetViewer(parent=self)
        self.plot = PTPlot3DWidget(PTPlot3D(parent=self), parent=self)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.tabs, 1, 1, 1, 1)
        layout.addWidget(self.list, 2, 1, 1, 1)
        layout.addWidget(self.plot, 1, 2, 2, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 2)