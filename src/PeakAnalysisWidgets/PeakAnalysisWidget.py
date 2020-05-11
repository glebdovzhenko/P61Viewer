from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel

from P61App import P61App


class PeakAnalysisWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel('This widget is not implemented yet.'))


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = PeakAnalysisWidget()
    app.show()
    sys.exit(q_app.exec_())
