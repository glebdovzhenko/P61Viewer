"""
EditableList.py
===============


"""
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant, QSize, pyqtSlot
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QListView, QAbstractItemView, QPushButton, QCheckBox, QGridLayout, QFileDialog
import numpy as np

from P61App import P61App
from ImportWidgets import FileImportWidget


class EditableListModel(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.q_app = P61App.instance()
        self._names, self._colors, self._status = None, None, None
        self._upd()

        self.q_app.dataRowsAppended.connect(self.on_rows_appended)
        self.q_app.dataRowsRemoved.connect(self.on_rows_removed)
        self.q_app.dataActiveChanged.connect(self.on_data_active)

    def _upd(self):
        self._names = self.q_app.get_screen_names()
        self._colors = self.q_app.get_screen_colors()
        self._status = self.q_app.get_active_status()

    @pyqtSlot()
    def on_rows_appended(self, n_rows=0):
        self._upd()
        self.dataChanged.emit(self.index(self._names.shape[0] - n_rows), self.index(self._names.shape[0]), [])

    @pyqtSlot()
    def on_rows_removed(self, rows=[]):
        self._upd()
        self.dataChanged.emit(self.index(0), self.index(self._names.shape[0]), [])

    @pyqtSlot()
    def on_data_active(self, rows=[]):
        self._upd()
        if rows:
            self.dataChanged.emit(self.index(min(rows)), self.index(max(rows)), [Qt.CheckStateRole])
        else:
            self.dataChanged.emit(self.index(0), self.index(0), [Qt.CheckStateRole])

    def rowCount(self, parent=None, *args, **kwargs):
        return self._names.shape[0]

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return QVariant()
        if not 0 <= ii.row() < self._names.shape[0]:
            return QVariant

        if role == Qt.DisplayRole:
            return self._names.loc[ii.row()]
        elif role == Qt.ForegroundRole:
            if self._status.loc[ii.row()]:
                return QColor(self._colors.loc[ii.row()])
            else:
                return QColor(0, 0, 0, 255)
        elif role == Qt.CheckStateRole:
            return Qt.Checked if self._status.loc[ii.row()] else Qt.Unchecked

    def setData(self, ii: QModelIndex, value, role=None):
        if not ii.isValid():
            return False

        if role == Qt.CheckStateRole:
            self.q_app.set_active_status(ii.row(), bool(value))
            return True
        return False

    def flags(self, index: QModelIndex) -> QVariant:
        return QAbstractListModel.flags(self, index) | Qt.ItemIsUserCheckable


class EditableListWidget(QWidget):
    def __init__(self, parent=None, *args):
        QWidget.__init__(self, parent, *args)
        self.q_app = P61App.instance()

        # list
        self._model = EditableListModel()
        self.list = QListView()
        self.list.setModel(self._model)
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # buttons and checkbox
        self.bplus = QPushButton('+')
        self.bminus = QPushButton('-')
        self.check_box = QCheckBox(' ')
        self.check_box.setTristate(False)
        self.bplus.setFixedSize(QSize(51, 32))
        self.bminus.setFixedSize(QSize(51, 32))
        self.bplus.clicked.connect(self.bplus_onclick)
        self.bminus.clicked.connect(self.bminus_onclick)
        self.check_box.clicked.connect(self.check_box_on_click)

        # layouts
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.check_box, 1, 1, 1, 1)
        layout.addWidget(self.bplus, 1, 3, 1, 1)
        layout.addWidget(self.bminus, 1, 4, 1, 1)
        layout.addWidget(self.list, 2, 1, 1, 4)

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

        FileImportWidget().open_files(files)

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
    app = EditableListWidget()
    app.show()
    sys.exit(q_app.exec_())
