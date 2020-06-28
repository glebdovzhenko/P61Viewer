from PyQt5.QtWidgets import QDialog, QAbstractItemView, QGridLayout, QPushButton, QLabel
import copy
import numpy as np

from P61App import P61App
from ListWidgets import ActiveList


class CopyPopUp(QDialog):
    """"""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.label_from = QLabel('From:')
        self.label_to = QLabel('To:')
        self.list_from = ActiveList(parent=self)
        self.list_to = ActiveList(parent=self, selection_mode=QAbstractItemView.ExtendedSelection)
        self.button_ok = QPushButton('Copy')

        self.setWindowTitle('Copy fit parameters')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.label_from, 1, 1, 1, 1)
        layout.addWidget(self.label_to, 1, 2, 1, 1)
        layout.addWidget(self.list_from, 2, 1, 1, 1)
        layout.addWidget(self.list_to, 2, 2, 1, 1)
        layout.addWidget(self.button_ok, 3, 1, 1, 2)

        self.button_ok.clicked.connect(self.on_button_ok)

    def on_button_ok(self):
        if self.q_app.get_selected_idx() == -1:
            pass
        else:
            idx_to = self.list_to.get_selection()
            result = copy.deepcopy(self.q_app.get_general_result(self.q_app.get_selected_idx()))
            result.chisqr = np.NaN
            self.q_app.data.loc[idx_to, 'GeneralFitResult'] = [copy.deepcopy(result) for _ in range(len(idx_to))]
            self.q_app.genFitResChanged.emit(idx_to)
        self.close()


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = CopyPopUp()
    app.show()
    sys.exit(q_app.exec())