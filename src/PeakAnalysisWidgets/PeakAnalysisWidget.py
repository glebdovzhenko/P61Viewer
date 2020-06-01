from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel

from P61App import P61App

from PeakAnalysisWidgets.PAPlotWidget import PAPlotWidget


class PeakAnalysisWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.plot = PAPlotWidget(parent=self)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.plot)


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = PeakAnalysisWidget()
    app.show()
    sys.exit(q_app.exec_())
