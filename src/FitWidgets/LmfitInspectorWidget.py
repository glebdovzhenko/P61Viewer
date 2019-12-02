from PyQt5.QtWidgets import QWidget, QGridLayout, QCheckBox, QLabel, QLineEdit

from P61App import P61App


class LmfitInspectorWidget(QWidget):
    """"""
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.checkboxes = dict()
        self.labels = dict()
        self.edits = dict()
        self.err_labels = dict()

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.update_repr()
        self.q_app.lmFitModelUpdated.connect(self.update_repr)
        self.q_app.selectedIndexChanged.connect(self.update_repr)

    def update_repr(self):
        for wd in (self.checkboxes, self.labels, self.edits, self.err_labels):
            for k in wd:
                self.grid.removeWidget(wd[k])
                wd[k].setParent(None)
                wd[k].deleteLater()
            wd.clear()

        model = self.q_app.params['LmFitModel']
        if self.q_app.params['SelectedIndex'] == -1:
            fit_results = None
        else:
            fit_results = self.q_app.data.loc[self.q_app.params['SelectedIndex'], 'FitResult']

        if (model is None) or (fit_results is None) or (self.q_app.params['SelectedIndex'] == -1):
            return

        for row, k in enumerate(fit_results.params):
            print(fit_results.params[k])
            self.checkboxes[k] = QCheckBox(parent=self)  # fit_results.params[k].vary
            self.labels[k] = QLabel(fit_results.params[k].name, parent=self)
            self.edits[k] = QLineEdit(str(fit_results.params[k].value), parent=self)
            self.err_labels[k] = QLabel(str(fit_results.params[k].stderr), parent=self)

            self.grid.addWidget(self.checkboxes[k], row + 1, 1, 1, 1)
            self.grid.addWidget(self.labels[k], row + 1, 2, 1, 1)
            self.grid.addWidget(self.edits[k], row + 1, 3, 1, 1)
            self.grid.addWidget(self.err_labels[k], row + 1, 4, 1, 1)

        self.setLayout(self.grid)


if __name__ == '__main__':
    import sys

    q_app = P61App(sys.argv)
    fw = LmfitInspectorWidget()
    fw.show()
    sys.exit(q_app.exec())