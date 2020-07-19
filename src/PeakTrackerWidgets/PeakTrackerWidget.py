from PyQt5.QtWidgets import QWidget, QGridLayout

from P61App import P61App

from PeakTrackerWidgets.AutoFindCWT import AutoFindCWTWidget
from PeakTrackerWidgets.AutoFind import AutoFindWidget
from DatasetManager import DatasetViewer
from PlotWidgets import PTPlot3D, PTPlot3DWidget


class PeakAnalysisWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.afw = AutoFindWidget(parent=self)
        self.afw_cwt = AutoFindCWTWidget(parent=self)
        self.list = DatasetViewer(parent=self)
        self.plot = PTPlot3DWidget(PTPlot3D(parent=self), parent=self)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.afw, 1, 1, 1, 1)
        layout.addWidget(self.afw_cwt, 2, 1, 1, 1)
        layout.addWidget(self.list, 3, 1, 1, 1)
        layout.addWidget(self.plot, 1, 2, 3, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 2)