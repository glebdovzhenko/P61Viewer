from PyQt5.QtWidgets import QWidget, QGridLayout, QCheckBox, QLabel, QLineEdit, QDoubleSpinBox

from P61App import P61App
from FitWidgets.FloatEditWidget import FloatEditWidget


class LmfitInspectorWidget(QWidget):
    """"""
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.checkboxes = dict()
        self.labels = dict()
        self.edits = dict()
        self.err_labels = dict()
        self.edit_slots = dict()

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.create_repr()
        self.q_app.lmFitModelUpdated.connect(self.create_repr)
        self.q_app.selectedIndexChanged.connect(self.create_repr)
        self.q_app.dataFitChanged.connect(self.on_fit_changed)

    def on_fit_changed(self, idx):
        if idx == self.q_app.params['SelectedIndex']:
            if len(self.checkboxes.keys()) == 0:
                self.create_repr()
            else:
                self.update_repr()

    def update_repr(self):
        fit_results = self.q_app.data.loc[self.q_app.params['SelectedIndex'], 'FitResult']

        for row, k in enumerate(fit_results.params):
            self.checkboxes[k].setChecked(fit_results.params[k].vary)

            if fit_results.params[k].stderr is not None:
                self.err_labels[k] = QLabel('± %.03E' % fit_results.params[k].stderr, parent=self)
            else:
                self.err_labels[k] = QLabel('', parent=self)

            self.edits[k].set_value(fit_results.params[k].value, emit=False)

    def create_repr(self):
        for wd in (self.checkboxes, self.labels, self.edits, self.err_labels):
            for k in wd:
                self.grid.removeWidget(wd[k])
                wd[k].setParent(None)
                wd[k].deleteLater()
            wd.clear()

        if self.q_app.params['SelectedIndex'] == -1:
            return

        fit_results = self.q_app.data.loc[self.q_app.params['SelectedIndex'], 'FitResult']

        if fit_results is None:
            return

        for row, k in enumerate(fit_results.params):
            self.checkboxes[k] = QCheckBox(parent=self)
            self.checkboxes[k].setChecked(fit_results.params[k].vary)
            self.checkboxes[k].stateChanged.connect(self.checkbox_slot_factory(k))

            self.labels[k] = QLabel(fit_results.params[k].name, parent=self)
            if fit_results.params[k].stderr is not None:
                self.err_labels[k] = QLabel('± %.03E' % fit_results.params[k].stderr, parent=self)
            else:
                self.err_labels[k] = QLabel('', parent=self)

            self.edits[k] = FloatEditWidget(fit_results.params[k].value)
            self.edits[k].valueUserUpd.connect(self.edit_slot_factory(k))

            self.grid.addWidget(self.checkboxes[k], row + 1, 1, 1, 1)
            self.grid.addWidget(self.labels[k], row + 1, 2, 1, 1)
            self.grid.addWidget(self.edits[k], row + 1, 3, 1, 1)
            self.grid.addWidget(self.err_labels[k], row + 1, 4, 1, 1)

    def edit_slot_factory(self, parameter):
        def slot(value):
            fr = self.q_app.data.loc[self.q_app.params['SelectedIndex'], 'FitResult']
            fr.params[parameter].set(value=value)
            self.q_app.dataFitChanged.emit(self.q_app.params['SelectedIndex'])
        return slot

    def checkbox_slot_factory(self, parameter):
        def slot(value):
            fr = self.q_app.data.loc[self.q_app.params['SelectedIndex'], 'FitResult']
            fr.params[parameter].set(vary=bool(value))
            self.q_app.dataFitChanged.emit(self.q_app.params['SelectedIndex'])
        return slot


if __name__ == '__main__':
    import sys

    q_app = P61App(sys.argv)
    fw = LmfitInspectorWidget()
    fw.show()
    sys.exit(q_app.exec())