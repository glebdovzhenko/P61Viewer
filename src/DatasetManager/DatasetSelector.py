from PyQt5.QtCore import Qt, QModelIndex, QSortFilterProxyModel
from PyQt5.QtWidgets import QWidget, QTableView, QAbstractItemView, QGridLayout

from P61App import P61App


class SelectorProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None, *args):
        QSortFilterProxyModel.__init__(self, parent)
        self.q_app = P61App.instance()
        self.selected = {k: True for k in self.q_app.data[self.q_app.data['Active']].index}

    def filterAcceptsRow(self, source_row, source_parent: QModelIndex):
        active = self.q_app.data.loc[source_row, 'Active']
        return True if active is None else active

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ['Select', 'Name'][section]

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return None

        if ii.column() == 0:
            if role == Qt.CheckStateRole:
                return Qt.Checked if self.selected[self.mapToSource(ii).row()] else Qt.Unchecked
            else:
                return None
        elif ii.column() == 1:
            if role == Qt.CheckStateRole:
                return None
            else:
                return QSortFilterProxyModel.data(self, self.index(ii.row(), 0), role)

    def flags(self, ii: QModelIndex):
        if not ii.isValid():
            return 0

        result = super(QSortFilterProxyModel, self).flags(ii)
        if ii.column() == 1:
            result ^= Qt.ItemIsUserCheckable
        elif ii.column() == 0:
            result |= Qt.ItemIsUserCheckable

        return result

    def setData(self, ii: QModelIndex, value, role=None):
        if not ii.isValid():
            return False

        if ii.column() == 0 and role == Qt.CheckStateRole:
            sr = self.mapToSource(ii).row()
            self.selected[sr] = bool(value)
            self.dataChanged.emit(ii, ii)
            return True
        else:
            return False


class DatasetSelector(QWidget):
    def __init__(self, parent=None, *args):
        QWidget.__init__(self, parent, *args)
        self.q_app = P61App.instance()

        self.view = QTableView()
        self.proxy = None

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.view, 1, 1, 1, 1)

        if self.q_app.data_model is None:
            self.q_app.dataModelSetUp.connect(self.setup_model)
        else:
            self.setup_model()

    def setup_model(self):
        self.proxy = SelectorProxyModel()
        self.proxy.setSourceModel(self.q_app.data_model)
        self.view.setModel(self.proxy)
        self.view.setSelectionBehavior(QTableView.SelectRows)
