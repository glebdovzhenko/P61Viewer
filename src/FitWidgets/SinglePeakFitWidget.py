from PyQt5.QtWidgets import QWidget
from P61BApp import P61BApp


class SinglePeakFitWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)




if __name__ == '__main__':
    import sys
    q_app = P61BApp(sys.argv)
    app = SinglePeakFitWidget()
    app.show()
    sys.exit(q_app.exec())