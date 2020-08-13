from PyQt5.QtWidgets import QWidget, QGridLayout

from P61App import P61App

from PeakTrackerWidgets.AutoFind import AutoFindWidget
from PeakTrackerWidgets.PeakFit import PeakFitWidget
from DatasetManager import DatasetViewer
from PlotWidgets import PTPlot3D, PTPlot3DWidget


class PeakAnalysisWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.afw = AutoFindWidget(parent=self)
        self.fit = PeakFitWidget(parent=self)
        self.list = DatasetViewer(parent=self)
        self.plot = PTPlot3DWidget(PTPlot3D(parent=self), parent=self)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.afw, 1, 1, 1, 1)
        layout.addWidget(self.list, 2, 1, 1, 1)
        layout.addWidget(self.fit, 1, 2, 2, 1)
        layout.addWidget(self.plot, 1, 3, 2, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 2)