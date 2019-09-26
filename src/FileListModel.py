from PyQt5.QtCore import QAbstractListModel, QModelIndex, QVariant, Qt
from PyQt5.QtGui import QColor
from src.SpectrumFileData import SpectrumFileData


class FileListModel(QAbstractListModel):
    color_cycle = ('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf')

    def __init__(self, parent=None):
        super().__init__(parent)
        self._histogram_list = []
        self._color_count = 0

    def _histogram(self, idx):
        return self._histogram_list[idx.row()]

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._histogram_list)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return QVariant(self._histogram_list[index.row()].short_name())
        elif role == Qt.ForegroundRole:
            if self._histogram_list[index.row()].show():
                return QColor(*self._histogram_list[index.row()].get_color(), 255)
            else:
                return QColor(0, 0, 0, 255)
        elif role == Qt.CheckStateRole:
            return Qt.Checked if self._histogram_list[index.row()].show() else Qt.Unchecked

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if not index.isValid():
            return False

        if role == Qt.CheckStateRole:
            self._histogram_list[index.row()].set_show_status(bool(value))
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index: QModelIndex):
        return QAbstractListModel.flags(self, index) | Qt.ItemIsUserCheckable

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(parent, row, row + count - 1)
        del self._histogram_list[row:row + count]
        self.endRemoveRows()
        return True

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertRows(parent, row, row + count - 1)
        self._histogram_list = self._histogram_list[:row] + [SpectrumFileData('') for _ in range(count)] + \
                               self._histogram_list[row:]
        self.endInsertRows()
        return True

    def _next_color(self):
        self._color_count += 1
        return self.color_cycle[self._color_count % len(self.color_cycle)]

    def get_names(self):
        return [x.get_name() for x in self._histogram_list]

    def data_to_plot(self):
        for ff in self._histogram_list:
            if ff.show():
                yield ff.plot_line

    def get_plot_show(self, idxs):
        return [bool(self.data(idx, role=Qt.CheckStateRole)) for idx in idxs]

    def update_plot_show(self, idxs, value):
        for idx in idxs:
            self._histogram_list[idx.row()].set_show_status(value)
        self.dataChanged.emit(min(idxs), max(idxs))

    def append_files(self, f_list):
        names = [x.get_name() for x in self._histogram_list]

        success, failed = [], []
        for ff in f_list:
            tmp0, tmp1 = SpectrumFileData(''), SpectrumFileData('')
            if tmp0.init_from_nexus(ff, 'channel00') and tmp1.init_from_nexus(ff, 'channel01'):
                success.extend([tmp0, tmp1])
            else:
                failed.append(ff)

        rc, fl = self.rowCount(), len(success)
        self.insertRows(rc, fl)
        for i in range(rc, rc + fl):
            self._histogram_list[i] = success[i - rc]
            self._histogram_list[i].set_plot_color(self._next_color())
        self.dataChanged.emit(self.index(rc, 0), self.index(rc + fl, 0))

        return failed
