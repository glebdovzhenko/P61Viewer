from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel

from P61App import P61App


class LmfitQuality(QWidget):
    """

    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.fit_results = None

        self.chisq_label = QLabel(u'')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.chisq_label, 1, 1, 1, 1)

        self.upd_fit_results()

        self.q_app.selectedIndexChanged.connect(self.upd_fit_results)
        self.q_app.dataFitChanged.connect(self.upd_fit_results)

    def upd_fit_results(self):
        if self.q_app.get_selected_idx() == -1:
            self.fit_results = None
        else:
            self.fit_results = self.q_app.get_function_fit_result(self.q_app.get_selected_idx())

        if self.fit_results is not None:
            if self.fit_results.chisqr is not None:
                self.chisq_label.setText(u'χ² = %.03E' % self.fit_results.chisqr)
            else:
                self.chisq_label.setText(u'')
        else:
            self.chisq_label.setText(u'')
