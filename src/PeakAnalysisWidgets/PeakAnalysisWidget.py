from PyQt5.QtWidgets import QWidget, QGridLayout

from P61App import P61App

from PeakAnalysisWidgets.AutoFindWidget import AutoFindWidget
from PlotWidgets import PAPlotWidget
from ListWidgets import ActiveListWidget


class PeakAnalysisWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.afw = AutoFindWidget(parent=self)
        self.plw = PAPlotWidget(parent=self)
        self.list = ActiveListWidget(parent=self)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.afw, 1, 1, 1, 1)
        layout.addWidget(self.plw, 1, 2, 4, 1)
        layout.addWidget(self.list, 4, 1, 1, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 3)