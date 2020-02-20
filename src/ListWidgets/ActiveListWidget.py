"""
ActiveList.py
=============


"""
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant, QItemSelectionModel, pyqtSlot
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QListView, QAbstractItemView, QGridLayout

from P61App import P61App


class ActiveListModel(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.q_app = P61App.instance()

        self._names, self._colors = None, None
        self._upd()

        # signals
        self.q_app.dataRowsAppended.connect(self.on_hists_added)
        self.q_app.dataRowsRemoved.connect(self.on_hists_removed)
        self.q_app.dataActiveChanged.connect(self.on_hists_ac)

    def rowCount(self, parent=None, *args, **kwargs):
        return self._names.shape[0]

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            return self._names.iloc[ii.row()]
        elif role == Qt.ForegroundRole:
            return QColor(self._colors.iloc[ii.row()])

    def _upd(self):
        self._names = self.q_app.get_screen_names(only_active=True)
        self._colors = self.q_app.get_screen_colors(only_active=True)

    @pyqtSlot()
    def on_hists_added(self, n_rows=0):
        self._upd()
        self.dataChanged.emit(self.index(0), self.index(self._names.shape[0]))

    @pyqtSlot()
    def on_hists_removed(self, rows=[]):
        self._upd()
        self.dataChanged.emit(self.index(0), self.index(self._names.shape[0]))

    @pyqtSlot()
    def on_hists_ac(self, rows=[]):
        self._upd()
        self.dataChanged.emit(self.index(0), self.index(self._names.shape[0]))

    def get_indices(self):
        return self._names.index


class ActiveListView(QListView):
    def __init__(self, parent=None):
        QListView.__init__(self, parent=parent)
        self.q_app = P61App.instance()

    @pyqtSlot()
    def dataChanged(self, topLeft, bottomRight, roles):
        QListView.dataChanged(self, topLeft, bottomRight, roles)
        self.update_selection_view()

    def update_selection_view(self):
        model_ids = self.model().get_indices()
        if len(model_ids) == 0:
            self.q_app.set_selected_idx(-1)
        elif self.q_app.get_selected_idx() not in model_ids:
            self.q_app.set_selected_idx(model_ids[0])
            self.selectionModel().select(self.model().index(0), QItemSelectionModel.ClearAndSelect)
        else:
            pass

    @pyqtSlot()
    def update_selection_model(self):
        ids = self.selectedIndexes()
        if not ids:
            self.q_app.set_selected_idx(-1)
        else:
            self.q_app.set_selected_idx(self.model().get_indices()[ids[0].row()])


class ActiveListWidget(QWidget):
    def __init__(self, parent=None, selection_mode=QAbstractItemView.SingleSelection, *args):
        QWidget.__init__(self, parent, *args)
        self.q_app = P61App.instance()

        # list
        self._model = ActiveListModel()
        self.list = ActiveListView()
        self.list.setModel(self._model)
        self.list.setSelectionMode(selection_mode)
        if selection_mode == QAbstractItemView.SingleSelection:
            self.list.selectionModel().selectionChanged.connect(self.list.update_selection_model)

        # layouts
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.list, 1, 1, 1, 1)

    def get_selection(self):
        ids = self.list.selectedIndexes()
        ai = self.q_app.get_active_ids()
        return [ai[idx.row()] for idx in ids]


if __name__ == '__main__':
    import sys
    from ListWidgets.EditableListWidget import EditableListWidget

    q_app = P61App(sys.argv)
    app = EditableListWidget()
    app.show()
    app2 = ActiveListWidget()
    app2.show()
    sys.exit(q_app.exec())
