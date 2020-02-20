from PyQt5.QtWidgets import QWidget, QGridLayout
from P61App import P61App


class PeakAnalysisWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        layout = QGridLayout()
        self.setLayout(layout)
