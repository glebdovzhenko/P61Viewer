"""
ActiveList.py
=============


"""
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant, QItemSelectionModel
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QListView, QAbstractItemView, QGridLayout

from P61App import P61App


class ActiveListModel(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.q_app = P61App.instance()
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

    def _upd(self):
        self._data = self.q_app.data
        self._active_idx = self.q_app.data[self.q_app.data['Active']].index

    def on_hists_added(self, n_rows):
        # TODO: redo
        self._upd()
        self.dataChanged.emit(self.index(0), self.index(self._data.shape[0]))

    def on_hists_removed(self, rows):
        # TODO: redo
        self._upd()
        self.dataChanged.emit(self.index(0), self.index(self._data.shape[0]))

    def on_hists_ac(self, rows):
        # TODO: redo
        self._upd()
        self.dataChanged.emit(self.index(0), self.index(self._data.shape[0]))


class ActiveListWidget(QWidget):
    def __init__(self, parent=None, selection_mode=QAbstractItemView.SingleSelection, *args):
        QWidget.__init__(self, parent, *args)
        self.q_app = P61App.instance()

        # list
        self._model = ActiveListModel()
        self.list = QListView()
        self.list.setModel(self._model)
        self.list.setSelectionMode(selection_mode)

        # layouts
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.list, 2, 1, 1, 4)

        # signals
        if selection_mode == QAbstractItemView.SingleSelection:
            self.list.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.q_app.dataRowsAppended.connect(self.update_selection)
        self.q_app.dataRowsRemoved.connect(self.update_selection)
        self.q_app.dataActiveChanged.connect(self.update_selection)

    def on_selection_changed(self):
        ids = self.list.selectedIndexes()
        if ids:
            self.q_app.params['SelectedIndex'] = self.q_app.data[self.q_app.data['Active']].index[ids[0].row()]
            self.q_app.selectedIndexChanged.emit(self.q_app.params['SelectedIndex'])

    def update_selection(self):
        active_idx = self.q_app.data[self.q_app.data['Active']].index
        if active_idx.shape[0] == 0:
            self.q_app.params['SelectedIndex'] = -1
            self.q_app.selectedIndexChanged.emit(-1)
        elif self.q_app.params['SelectedIndex'] in active_idx:
            self.q_app.selectedIndexChanged.emit(self.q_app.params['SelectedIndex'])
        else:
            self.q_app.params['SelectedIndex'] = active_idx[0]
            self.q_app.selectedIndexChanged.emit(active_idx[0])
            self.list.selectionModel().select(self._model.index(0), QItemSelectionModel.Select)

    def set_selection(self):
        if self.q_app.params['SelectedIndex'] != -1:
            self.list.selectionModel().select(
                self._model.index(self.q_app.params['SelectedIndex']), QItemSelectionModel.Select)

    def get_selection(self):
        ids = self.list.selectedIndexes()
        return [self.q_app.data[self.q_app.data['Active']].index[idx.row()] for idx in ids]


if __name__ == '__main__':
    import sys
    from ListWidgets.EditableListWidget import EditableListWidget

    q_app = P61App(sys.argv)
    app = EditableListWidget()
    app.show()
    app2 = ActiveListWidget()
    app2.show()
    sys.exit(q_app.exec())
