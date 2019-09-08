from PyQt5.QtWidgets import QWidget, QApplication, QAbstractItemView, QPushButton, QGridLayout, QTableView, QFileDialog, QErrorMessage
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt, QSize

import os
import pandas as pd
import h5py
import json


class SpectrumFileData:
    def __init__(self, name):
        self._name = name
        self._show = True
        self.plot_color = None
        self.spectrum_data = None
        self.spectrum_metadata = None

    def short_name(self):
        tmp = os.path.basename(self._name)
        if len(tmp) > 10:
            return '...' + tmp[-10:]
        else:
            return '.../' + tmp

    def show(self):
        return self._show

    def change_show_status(self):
        self._show = not self._show

    def set_name(self, new_name):
        self._name = new_name

    def get_name(self):
        return self._name

    def __repr__(self):
        return ('x' if self.show() else 'o') + ' ' + self.short_name()

    def init_from_h5(self, f_name):
        # TODO: ???
        try:
            with h5py.File(f_name, 'r') as f:
                self.spectrum_data = pd.DataFrame(f['Spectrum'][:], columns=['keV', 'Int'])
                self.spectrum_metadata = json.loads(f['Metadata'][()])
                self.set_name(f_name)
                return True
        except Exception as e:
            return False


class FileTableModel(QAbstractTableModel):
    def __init__(self, init_data, parent=None):
        super().__init__(parent)
        self.file_data_list = init_data.copy()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.file_data_list)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 0:
                return QVariant(self.file_data_list[index.row()].short_name())
        elif role == Qt.CheckStateRole:
            if index.column() == 0:
                return Qt.Checked if self.file_data_list[index.row()].show() else Qt.Unchecked

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if not index.isValid():
            return False

        if role == Qt.CheckStateRole:
            self.file_data_list[index.row()].change_show_status()
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index: QModelIndex):
        return QAbstractTableModel.flags(self, index) | Qt.ItemIsUserCheckable

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(parent, row, row + count - 1)
        del self.file_data_list[row:row + count]
        self.endRemoveRows()
        return True

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertRows(parent, row, row + count - 1)
        self.file_data_list = self.file_data_list[:row] + [SpectrumFileData('') for _ in range(count)] + \
                              self.file_data_list[row:]
        self.endInsertRows()
        return True

    def append_files(self, f_list):
        rc, fl = self.rowCount(), len(f_list)
        self.insertRows(rc, fl)
        for i in range(rc, rc + fl):
            self.file_data_list[i] = f_list[i - rc]
        self.dataChanged.emit(self.index(rc, 0), self.index(rc + fl, 0))

    def get_names(self):
        return [x.get_name() for x in self.file_data_list]

    def data_to_plot(self):
        for ff in self.file_data_list:
            if ff.show():
                yield ff.spectrum_data


class FileListWidget(QWidget):
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)

        default_list = []
        self.file_opener = lambda *xs: True  # int(xs[0][-4]) % 2

        # List model - view
        self.table_model = FileTableModel(default_list)
        self.table_view = QTableView()
        self.table_view.setSelectionMode(QAbstractItemView.MultiSelection)
        self.table_view.setModel(self.table_model)

        # buttons
        bplus = QPushButton('+')
        bminus = QPushButton('-')
        bplus.setFixedSize(QSize(51, 32))
        bminus.setFixedSize(QSize(51, 32))
        bplus.clicked.connect(self.bplus_onclick)
        bminus.clicked.connect(self.bminus_onclick)

        layout = QGridLayout()
        layout.addWidget(bplus, 1, 2, 1, 1)
        layout.addWidget(bminus, 1, 3, 1, 1)
        layout.addWidget(self.table_view, 2, 1, 1, 3)
        self.setLayout(layout)

    def set_file_opener(self, fn):
        self.file_opener = fn

    def bminus_onclick(self):
        rows = [i.row() for i in self.table_view.selectedIndexes()]
        for i in sorted(rows, reverse=True):
            self.table_model.removeRow(i)

    def bplus_onclick(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Add spectra', '', 'All Files (*);;HDF5 files (*.h5)',
                                                options=QFileDialog.Options())
        files = [ff for ff in files if ff not in self.table_model.get_names()]

        success, failed = [], []
        for ff in files:
            tmp = SpectrumFileData('')
            if tmp.init_from_h5(ff):
                success.append(tmp)
            else:
                failed.append(ff)

        if failed:
            msg = QErrorMessage()
            msg.showMessage('Could not open files:\n' + '\n'.join(failed))
            msg.exec_()

        self.table_model.append_files(success)


if __name__ == '__main__':
    import sys
    qapp = QApplication(sys.argv)
    app = FileListWidget()
    app.show()
    sys.exit(qapp.exec_())
