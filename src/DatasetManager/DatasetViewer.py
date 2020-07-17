from PyQt5.QtCore import Qt, QModelIndex, QSortFilterProxyModel
from PyQt5.QtWidgets import QTableView, QAbstractItemView

from P61App import P61App


class ViewerProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None, *args):
        QSortFilterProxyModel.__init__(self, parent)
        self.q_app = P61App.instance()

    def filterAcceptsRow(self, source_row, source_parent: QModelIndex):
        active = self.q_app.data.loc[source_row, 'Active']
        return True if active is None else active

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return None

        if ii.column() == 0 and role == Qt.CheckStateRole:
            return None
        else:
            return super(QSortFilterProxyModel, self).data(ii, role)

    def flags(self, ii: QModelIndex):
        if not ii.isValid():
            return 0

        result = super(QSortFilterProxyModel, self).flags(ii)
        if ii.column() == 0:
            result ^= Qt.ItemIsUserCheckable

        return result


class DatasetViewer(QTableView):
    def __init__(self, parent=None, *args):
        QTableView.__init__(self, parent, *args)
        self.q_app = P61App.instance()

        self.proxy = None

        if self.q_app.data_model is None:
            self.q_app.dataModelSetUp.connect(self.setup_model)
        else:
            self.setup_model()

    def setup_model(self):
        self.proxy = ViewerProxyModel()
        self.proxy.setSourceModel(self.q_app.data_model)
        self.setModel(self.proxy)
        self.setColumnHidden(1, True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)

    def on_selection_changed(self):
        si = self.selectedIndexes()
        if si:
            idx, _ = si
            self.q_app.set_selected_idx(self.model().index(idx.row(), 0).row())
