from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton
import logging

from P61App import P61App
from DatasetManager import DatasetSelector


class InitPopUp(QDialog):
    """"""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        self.q_app = P61App.instance()
        self.logger = logging.getLogger(str(self.__class__))

        self.list_to = DatasetSelector(parent=self)
        self.button_ok = QPushButton('Init')

        self.setWindowTitle('Initiate fit models from peak data')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.list_to, 1, 1, 1, 1)
        layout.addWidget(self.button_ok, 2, 1, 1, 1)

        self.button_ok.clicked.connect(self.on_button_ok)

    def on_button_ok(self):
        if self.q_app.get_selected_idx() == -1:
            pass
        else:
            idx_to = [k for k in self.list_to.proxy.selected if self.list_to.proxy.selected[k]]
            for idx in idx_to:
                self.parent().init_from_peaklist(idx)
        self.close()


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = InitPopUp()
    app.show()
    sys.exit(q_app.exec())
