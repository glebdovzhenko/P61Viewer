from PyQt5.QtWidgets import QWidget, QGridLayout

from P61App import P61App

from PeakAnalysisWidgets.AutoFind import AutoFindWidget
from PlotWidgets import PAPlot
from DatasetManager import DatasetViewer


class PeakAnalysisWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.afw = AutoFindWidget(parent=self)
        self.plw = PAPlot(parent=self)
        self.list = DatasetViewer(parent=self)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.afw, 1, 1, 1, 1)
        layout.addWidget(self.plw, 1, 2, 4, 1)
        layout.addWidget(self.list, 4, 1, 1, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 2)