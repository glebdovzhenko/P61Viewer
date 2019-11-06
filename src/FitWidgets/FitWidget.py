from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

from P61BApp import P61BApp
from ListWidgets import ActiveListWidget
from FitWidgets.FitModelInspectorWidget import LmFitInspectorWidget
from FitWidgets.FitModelBuilderWidget import FitModelBuilderWidget


class FitWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61BApp.instance()

        self.lmfit_builder = FitModelBuilderWidget()
        self.lmfit_inspector = LmFitInspectorWidget(parent=self)

        self.active_list = ActiveListWidget()

        self.fit_btn = QPushButton('Fit this')
        self.fit_all_btn = QPushButton('Fit all')
        self.copy_btn = QPushButton('Copy params')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.lmfit_builder, 1, 1, 1, 3)
        layout.addWidget(self.lmfit_inspector, 2, 1, 1, 3)
        layout.addWidget(self.active_list, 3, 2, 3, 2)
        layout.addWidget(self.fit_btn, 3, 1, 1, 1)
        layout.addWidget(self.fit_all_btn, 4, 1, 1, 1)
        layout.addWidget(self.copy_btn, 5, 1, 1, 1)


if __name__ == '__main__':
    import sys
    q_app = P61BApp(sys.argv)
    app = FitWidget()
    app.show()
    sys.exit(q_app.exec())