from PyQt5.QtWidgets import QDialog, QAbstractItemView, QGridLayout, QPushButton, QLabel, QComboBox, QProgressDialog
from PyQt5.Qt import Qt
import copy

from P61App import P61App
from ListWidgets import ActiveListWidget


class SeqFitPopUpWidget(QDialog):
    """"""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.current_name = QLabel(parent=self)
        self.combo = QComboBox(parent=self)
        self.combo.addItems(['Do not init', 'Init all from current', 'Sequential from current'])
        self.btn_ok = QPushButton('Fit', parent=self)
        self.selection_list = ActiveListWidget(parent=self, selection_mode=QAbstractItemView.ExtendedSelection)

        self.setWindowTitle('Fit multiple spectra')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.combo, 1, 1, 1, 1)
        layout.addWidget(self.current_name, 2, 1, 1, 1)
        layout.addWidget(self.btn_ok, 3, 1, 1, 1)
        layout.addWidget(self.selection_list, 1, 2, 3, 1)

        self.btn_ok.clicked.connect(self.on_btn_ok)
        self.combo.currentIndexChanged.connect(self.on_combo_index_change)

    def on_combo_index_change(self):
        if self.q_app.params['SelectedIndex'] == -1:
            return
        if self.combo.currentIndex() in (1, 2):
            self.current_name.setText(self.q_app.data.loc[self.q_app.params['SelectedIndex'], 'ScreenName'])
        else:
            self.current_name.setText('')

    def on_btn_ok(self):
        if self.q_app.params['SelectedIndex'] == -1:
            self.close()

        fit_ids = list(self.selection_list.get_selection())
        fit_type = self.combo.currentIndex()

        if fit_type == 1:
            self.q_app.data.loc[fit_ids, 'FitResult'] = [self.q_app.data.loc[self.q_app.params['SelectedIndex'],
                                                                             'FitResult']] * len(fit_ids)

        # TODO: add cancel functionality
        progress = QProgressDialog("Sequential Fit", "Cancel", 0, len(fit_ids))
        progress.setWindowModality(Qt.WindowModal)
        for ii, (prev_idx, idx) in enumerate(zip([self.q_app.params['SelectedIndex']] + fit_ids[:-1], fit_ids)):
            progress.setValue(ii)
            if fit_type == 2:
                self.q_app.data.loc[idx, 'FitResult'] = copy.copy(self.q_app.data.loc[prev_idx, 'FitResult'])
            self.parent().on_fit_btn(idx=idx)
        progress.setValue(len(fit_ids))
        self.close()