"""
EditableList.py
===============


"""
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, QSize, pyqtSlot
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QTableView, QAbstractItemView, QPushButton, QCheckBox, QGridLayout, QFileDialog
import numpy as np

from P61App import P61App
from IOWidgets import FileImport, FileExport


class MainFileListModel(QAbstractTableModel):
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.q_app = P61App.instance()
        self._data = None
        self._upd()

        self.q_app.dataRowsAppended.connect(self.on_rows_appended)
        self.q_app.dataRowsRemoved.connect(self.on_rows_removed)
        self.q_app.dataActiveChanged.connect(self.on_data_active)

    def _upd(self):
        self._data = self.q_app.data[['ScreenName', 'Color', 'Active', 'DeadTime']]

    @pyqtSlot()
    def on_rows_appended(self, n_rows=0):
        self._upd()
        self.modelReset.emit()
        # TODO: make work faster

    @pyqtSlot()
    def on_rows_removed(self, rows=[]):
        self._upd()
        self.modelReset.emit()

    @pyqtSlot()
    def on_data_active(self, rows=[]):
        self._upd()
        self.modelReset.emit()

    def rowCount(self, parent=None, *args, **kwargs):
        return self._data.shape[0]

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ['File', u'💀⏱'][section]
        return None

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return QVariant()

        if ii.column() == 0:
            if role == Qt.DisplayRole:
                return self._data['ScreenName'].loc[ii.row()]
            elif role == Qt.ForegroundRole:
                if self._data['Active'].loc[ii.row()]:
                    return QColor(self._data['Color'].loc[ii.row()])
                else:
                    return QColor(0, 0, 0, 255)
            elif role == Qt.CheckStateRole:
                return Qt.Checked if self._data['Active'].loc[ii.row()] else Qt.Unchecked
        elif ii.column() == 1:
            if role == Qt.DisplayRole:
                dt = self._data['DeadTime'].loc[ii.row()]
                return '%.03f' % dt if dt is not None else ''

    def setData(self, ii: QModelIndex, value, role=None):
        if not ii.isValid():
            return False

        if role == Qt.CheckStateRole and ii.column() == 0:
            self.q_app.set_active_status(ii.row(), bool(value))
            return True

        return False

    def flags(self, index: QModelIndex) -> QVariant:
        if index.column() == 0:
            return QAbstractTableModel.flags(self, index) | Qt.ItemIsUserCheckable
        else:
            return QAbstractTableModel.flags(self, index)


class MainFileList(QWidget):
    def __init__(self, parent=None, *args):
        QWidget.__init__(self, parent, *args)
        self.q_app = P61App.instance()

        # list
        self._model = MainFileListModel()
        self.list = QTableView()
        self.list.setModel(self._model)
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.setSelectionBehavior(QTableView.SelectRows)

        # buttons and checkbox
        self.bplus = QPushButton('+')
        self.bminus = QPushButton('-')
        self.check_box = QCheckBox(' ')
        self.bexport = QPushButton('Export')
        self.check_box.setTristate(False)
        self.bplus.setFixedSize(QSize(51, 32))
        self.bminus.setFixedSize(QSize(51, 32))
        self.bplus.clicked.connect(self.bplus_onclick)
        self.bminus.clicked.connect(self.bminus_onclick)
        self.bexport.clicked.connect(self.bexport_onclick)
        self.check_box.clicked.connect(self.check_box_on_click)

        # layouts
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.check_box, 1, 1, 1, 1)
        layout.addWidget(self.bplus, 1, 3, 1, 1)
        layout.addWidget(self.bminus, 1, 4, 1, 1)
        layout.addWidget(self.list, 2, 1, 1, 4)
        layout.addWidget(self.bexport, 3, 3, 1, 2)

        # signal handlers
        self.list.selectionModel().selectionChanged.connect(self.check_box_update)
        self.q_app.dataActiveChanged.connect(self.check_box_update)

    def bminus_onclick(self):
        rows = [idx.row() for idx in self.list.selectedIndexes()]
        self.list.clearSelection()
        self.q_app.data.drop(rows, inplace=True)
        self.q_app.data.set_index(np.arange(self.q_app.data.shape[0]), inplace=True)
        self.q_app.dataRowsRemoved.emit(rows)

    def bplus_onclick(self):
        fd = QFileDialog()
        files, _ = fd.getOpenFileNames(
            self,
            'Add spectra',
            '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/pwdr_h5',
            'All Files (*);;NEXUS files (*.nxs)',
            options=QFileDialog.Options()
        )

        FileImport().open_files(files)

    def bexport_onclick(self):
        fd = QFileDialog()
        fd.setOption(fd.ShowDirsOnly, True)
        dd = fd.getExistingDirectory(self, caption='Export spectra to')

        rows = [idx.row() for idx in self.list.selectedIndexes()]
        FileExport().to_csvs(dd, rows)

    def check_box_on_click(self):
        self.check_box.setTristate(False)
        rows = [idx.row() for idx in self.list.selectedIndexes()]
        for row in rows:
            self.q_app.set_active_status(row, bool(self.check_box.checkState()), emit=False)
        self.q_app.dataActiveChanged.emit(rows)

    def check_box_update(self):
        rows = [idx.row() for idx in self.list.selectedIndexes()]
        status = self.q_app.get_active_status()
        status = status[rows]

        if all(status):
            self.check_box.setCheckState(Qt.Checked)
        elif not any(status):
            self.check_box.setCheckState(Qt.Unchecked)
        else:
            self.check_box.setCheckState(Qt.PartiallyChecked)


if __name__ == '__main__':
    import sys

    q_app = P61App(sys.argv)
    app = MainFileList()
    app.show()
    sys.exit(q_app.exec_())
