from PyQt5.QtWidgets import QDialog, QAbstractItemView, QGridLayout, QPushButton, QLabel
import copy

from P61App import P61App
from ListWidgets import ActiveListWidget


class PopUpCopyWidget(QDialog):
    """"""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.label_from = QLabel('From:')
        self.label_to = QLabel('To:')
        # self.list_from = QListWidget(parent=self)
        self.list_from = ActiveListWidget(parent=self)
        # self.list_to = QListWidget(parent=self)
        self.list_to = ActiveListWidget(parent=self, selection_mode=QAbstractItemView.ExtendedSelection)
        self.button_ok = QPushButton('Copy')

        self.setWindowTitle('Copy fit parameters')
        # self.list_from.set_selection()
        self.list_from.on_selected_index_changed(self.q_app.params['SelectedIndex'])

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.label_from, 1, 1, 1, 1)
        layout.addWidget(self.label_to, 1, 2, 1, 1)
        layout.addWidget(self.list_from, 2, 1, 1, 1)
        layout.addWidget(self.list_to, 2, 2, 1, 1)
        layout.addWidget(self.button_ok, 3, 1, 1, 2)

        self.button_ok.clicked.connect(self.on_button_ok)

    def on_button_ok(self):
        if self.q_app.params['SelectedIndex'] == -1:
            pass
        else:
            idx_to = self.list_to.get_selection()
            self.q_app.data.loc[idx_to, 'FitResult'] = [copy.deepcopy(
                self.q_app.data.loc[self.q_app.params['SelectedIndex'], 'FitResult']) for _ in range(len(idx_to))]
            self.q_app.dataFitChanged.emit(idx_to)
        self.close()


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = PopUpCopyWidget()
    app.show()
    sys.exit(q_app.exec())