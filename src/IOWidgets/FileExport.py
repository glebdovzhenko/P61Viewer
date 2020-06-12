from PyQt5.QtWidgets import QWidget, QMessageBox
import pandas as pd
import os

from P61App import P61App


class FileExport(QWidget):
    """
    Module responsible for exporting data
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

    def to_csvs(self, dirname, rows):
        rows = list(sorted(rows))
        names = self.q_app.data.loc[rows, 'ScreenName'].apply(lambda x: x.replace(':', '_').replace('.', '_') + '.csv')
        overlap = set(os.listdir(dirname)) & set(names)
        ret = QMessageBox.Ok

        if overlap:
            msg = QMessageBox(self)
            msg.setText('Warning! The following files will be overwritten')
            msg.setInformativeText('\n'.join(sorted(overlap)))
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = msg.exec()

        if ret == QMessageBox.Ok:
            for ii in rows:
                data = self.q_app.data.loc[ii, ['DataX', 'DataY', 'ScreenName']]
                f_name = data['ScreenName'].replace(':', '_').replace('.', '_') + '.csv'
                data = pd.DataFrame(data={'eV': 1E3 * data['DataX'], 'counts': data['DataY']})
                data = data[['eV', 'counts']]
                data.to_csv(os.path.join(dirname, f_name), header=True, index=False)