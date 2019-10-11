from PyQt5.QtCore import QAbstractListModel, QModelIndex, QVariant, Qt, pyqtSignal, QSortFilterProxyModel
from PyQt5.QtGui import QColor
from NexusHistogram import NexusHistogram
from AppState import AppState
import os


class HistogramListModel(QAbstractListModel):
    color_cycle = ('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf')
    filesAdded = pyqtSignal()

    def __init__(self, app_state: AppState, parent=None):
        super().__init__(parent)
        self._histogram_list = []
        self._color_count = 0
        self.app_state = app_state

    def rowCount(self, parent=QModelIndex()) -> int:
        # return len(self._histogram_list)
        return self.app_state.histogram_list_len()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return QVariant(self.app_state.get_histogram(index.row()).name)
            # return QVariant(self._histogram_list[index.row()].name)
        elif role == Qt.ForegroundRole:
            # if self._histogram_list[index.row()].active:
            if self.app_state.get_histogram(index.row()).active:
                return QColor(*self.app_state.get_histogram(index.row()).plot_color_qt, 255)
                # return QColor(*self._histogram_list[index.row()].plot_color_qt, 255)
            else:
                return QColor(0, 0, 0, 255)
        elif role == Qt.CheckStateRole:
            return Qt.Checked if self.app_state.get_histogram(index.row()).active else Qt.Unchecked
            # return Qt.Checked if self._histogram_list[index.row()].active else Qt.Unchecked

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if not index.isValid():
            return False

        if role == Qt.CheckStateRole:
            # self._histogram_list[index.row()].active = bool(value)
            self.app_state.get_histogram(index.row()).active = bool(value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index: QModelIndex):
        return QAbstractListModel.flags(self, index) | Qt.ItemIsUserCheckable

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(parent, row, row + count - 1)
        # del self._histogram_list[row:row + count]
        self.app_state.del_histograms(row, row + count)
        self.endRemoveRows()
        return True

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertRows(parent, row, row + count - 1)
        # self._histogram_list = self._histogram_list[:row] + [NexusHistogram() for _ in range(count)] + \
        #                        self._histogram_list[row:]
        self.app_state.insert_histograms(row, count)

        self.endInsertRows()
        return True

    def _next_color(self):
        self._color_count += 1
        return self.color_cycle[self._color_count % len(self.color_cycle)]

    def get_active(self, idxs):
        return [bool(self.data(idx, role=Qt.CheckStateRole)) for idx in idxs]

    def update_active(self, idxs, value):
        for idx in idxs:
            # self._histogram_list[idx.row()].active = value
            self.app_state.get_histogram(idx.row()).active = value
        if idxs:
            self.dataChanged.emit(min(idxs), max(idxs))

    def append_files(self, f_list):
        ids = self.app_state.get_hist_ids()
        ch0, ch1 = 'entry/instrument/xspress3/channel00/histogram', 'entry/instrument/xspress3/channel01/histogram'

        success, failed = [], []
        for ff in f_list:
            if (ff + ':' + ch0) not in ids:
                tmp0 = NexusHistogram()
                if tmp0.fill(ff, ch0, os.path.basename(ff) + ':ch0'):
                    success.append(tmp0)
                else:
                    failed.append(ff)

            if (ff + ':' + ch1) not in ids:
                tmp1 = NexusHistogram()
                if tmp1.fill(ff, ch1, os.path.basename(ff) + ':ch1'):
                    success.append(tmp1)
                else:
                    failed.append(ff)

        rc, fl = self.rowCount(), len(success)
        self.insertRows(rc, fl)
        for i in range(rc, rc + fl):
            # self._histogram_list[i] = success[i - rc]
            # self._histogram_list[i].plot_color_mpl = self._next_color()
            self.app_state.set_histogram(i, success[i - rc])
            self.app_state.get_histogram(i).plot_color_mpl = self._next_color()

        if success:
            self.dataChanged.emit(self.index(rc, 0), self.index(rc + fl, 0))
            self.filesAdded.emit()

        return failed

    def remove_files(self, idx):
        rows = [i.row() for i in idx]
        for i in sorted(rows, reverse=True):
            self.removeRow(i)
        self.dataChanged.emit(min(idx), max(idx))

    def is_active(self, row):
        return self.app_state.get_histogram(row).active
        # return self._histogram_list[row].active

