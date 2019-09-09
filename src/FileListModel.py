from PyQt5.QtCore import QAbstractListModel, QModelIndex, QVariant, Qt
from src.SpectrumFileData import SpectrumFileData


class FileListModel(QAbstractListModel):
    def __init__(self, init_data, parent=None):
        super().__init__(parent)
        self.file_data_list = init_data.copy()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.file_data_list)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return QVariant(self.file_data_list[index.row()].short_name())
        elif role == Qt.CheckStateRole:
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
        return QAbstractListModel.flags(self, index) | Qt.ItemIsUserCheckable

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
