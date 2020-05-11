from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from P61App import P61App
from ListWidgets import ActiveListWidget


class CorrectionWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel('This widget is not implemented yet.'))


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = CorrectionWidget()
    app.show()
    sys.exit(q_app.exec_())
