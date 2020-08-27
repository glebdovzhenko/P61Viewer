from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QColor
import pandas as pd
import logging


class DataSetStorageModel(QAbstractTableModel):
    def __init__(self, parent=None, instance=None):
        QAbstractTableModel.__init__(self, parent)

        self.q_app = instance
        self.logger = logging.getLogger(str(self.__class__))

        self.c_names = ['Name', u'💀⏱', u'χ²']

        self.q_app.genFitResChanged.connect(self.on_gen_fit_changed)

    def on_gen_fit_changed(self, rows):
        self.logger.debug('on_gen_fit_changed: Handling genFitResChanged(%s)' % (str(rows),))
        if rows:
            self.dataChanged.emit(
                self.index(min(rows), 2),
                self.index(max(rows), 2)
            )

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    def rowCount(self, parent=None, *args, **kwargs):
        return self.q_app.data.shape[0]

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.c_names[section]

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return None

        item_row = self.q_app.data.loc[ii.row()]

        if ii.column() == 0:
            if role == Qt.DisplayRole:
                return item_row['ScreenName']
            elif role == Qt.CheckStateRole:
                return Qt.Checked if item_row['Active'] else Qt.Unchecked
            elif role == Qt.ForegroundRole:
                if item_row['Active']:
                    return QColor(item_row['Color'])
                else:
                    return QColor('Black')
            else:
                return None
        elif ii.column() == 1:
            if role == Qt.DisplayRole:
                return item_row['DeadTime']
            else:
                return None
        elif ii.column() == 2:
            if role == Qt.DisplayRole:
                if item_row['GeneralFitResult'] is not None:
                    if item_row['GeneralFitResult'].chisqr is not None:
                        return '%.01f' % item_row['GeneralFitResult'].chisqr
                    else:
                        return None
                else:
                    return None
            else:
                return None
        else:
            return None

    def flags(self, ii: QModelIndex):
        if not ii.isValid():
            return 0

        result = super(QAbstractTableModel, self).flags(ii)

        if ii.column() == 0:
            result |= Qt.ItemIsUserCheckable

        return result

    def insertRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginInsertRows(parent, position, position + rows - 1)
        self.q_app.insert_rows(position, rows)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginRemoveRows(parent, position, position + rows - 1)
        self.q_app.remove_rows(position, rows)
        self.endRemoveRows()
        return True

    def setData(self, ii: QModelIndex, value, role=None):
        if ii.column() == 0 and role == Qt.CheckStateRole:
            self.q_app.set_active_status(ii.row(), bool(value))
            self.dataChanged.emit(ii, ii)
            return True
        else:
            return False

    def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
        tmp = {0: 'ScreenName', 1: 'DeadTime', 2: 'ScreenName'}
        self.q_app.sort_data(by=tmp[column], inplace=True, ascending=bool(order))
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount(), self.columnCount())
        )