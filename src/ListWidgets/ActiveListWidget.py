from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant, QItemSelectionModel
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QListView, QAbstractItemView, QGridLayout

from P61BApp import P61BApp


class ActiveListModel(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.q_app = P61BApp.instance()
        self._data = self.q_app.data
        self._active_idx = self.q_app.data[self.q_app.data['Active']].index

        self.q_app.dataRowsAppended.connect(self.on_hists_added)
        self.q_app.dataRowsRemoved.connect(self.on_hists_removed)
        self.q_app.dataActiveChanged.connect(self.on_hists_ac)

    def rowCount(self, parent=None, *args, **kwargs):
        return self._active_idx.shape[0]

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return QVariant()

        a_row = self._active_idx[ii.row()]
        if role == Qt.DisplayRole:
            return self._data.loc[a_row, 'ScreenName']
        elif role == Qt.ForegroundRole:
            return QColor(self._data.loc[a_row, 'Color'])

    def update_selection(self):
        if self._active_idx.shape[0] == 0:
            self.q_app.params['SelectedIndex'] = -1
            self.q_app.selectedIndexChanged.emit(-1)
        elif self.q_app.params['SelectedIndex'] in self._active_idx:
            self.q_app.selectedIndexChanged.emit(self.q_app.params['SelectedIndex'])
        else:
            self.q_app.params['SelectedIndex'] = self._active_idx[0]
            self.q_app.selectedIndexChanged.emit(self._active_idx[0])

    def _upd(self):
        self._data = self.q_app.data
        self._active_idx = self.q_app.data[self.q_app.data['Active']].index

    def on_hists_added(self, n_rows):
        # TODO: redo
        self._upd()
        self.update_selection()
        self.dataChanged.emit(self.index(0), self.index(self._data.shape[0]))

    def on_hists_removed(self, rows):
        # TODO: redo
        self._upd()
        self.update_selection()
        self.dataChanged.emit(self.index(0), self.index(self._data.shape[0]))

    def on_hists_ac(self, rows):
        # TODO: redo
        self._upd()
        self.update_selection()
        self.dataChanged.emit(self.index(0), self.index(self._data.shape[0]))


class ActiveListWidget(QWidget):
    def __init__(self, parent=None, *args):
        QWidget.__init__(self, parent, *args)
        self.q_app = P61BApp.instance()

        # list
        self._model = ActiveListModel()
        self.list = QListView()
        self.list.setModel(self._model)
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)

        # layouts
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.list, 2, 1, 1, 4)

        # signals
        self.list.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.q_app.selectedIndexChanged.connect(self.on_active_changed)

    def on_selection_changed(self):
        ids = self.list.selectedIndexes()
        if ids:
            self.q_app.params['SelectedIndex'] = self.q_app.data[self.q_app.data['Active']].index[ids[0].row()]
            self.q_app.selectedIndexChanged.emit(self.q_app.params['SelectedIndex'])

    def on_active_changed(self, n_row):
        # TODO: this handler is being called each time on_selection_changed is called
        self.list.selectionModel().select(self._model.index(n_row), QItemSelectionModel.Select)


if __name__ == '__main__':
    import sys
    from ListWidgets.EditableListWidget import EditableListWidget

    q_app = P61BApp(sys.argv)
    app = EditableListWidget()
    app.show()
    app2 = ActiveListWidget()
    app2.show()
    sys.exit(q_app.exec())
