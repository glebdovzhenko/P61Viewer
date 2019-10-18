from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QListView, QAbstractItemView, QGridLayout

from P61BApp import P61BApp


class ActiveListModel(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)

        P61BApp.instance().project.histsAdded.connect(self.on_hists_added)
        P61BApp.instance().project.histsRemoved.connect(self.on_hists_removed)
        P61BApp.instance().project.histsActiveChanged.connect(self.on_hists_ac)

    def rowCount(self, parent=None, *args, **kwargs):
        return P61BApp.instance().project.histogram_list_len(active=True)

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return QVariant()

        row = ii.row()

        if role == Qt.DisplayRole:
            return QVariant(P61BApp.instance().project.get_active_histogram(row).name)
        elif role == Qt.ForegroundRole:
            if P61BApp.instance().project.get_active_histogram(row).active:
                return QColor(*P61BApp.instance().project.get_active_histogram(row).plot_color_qt, 255)
            else:
                return QColor(0, 0, 0, 255)

    def on_hists_added(self):
        self.dataChanged.emit(self.index(0), self.index(self.rowCount()))

    def on_hists_removed(self):
        self.dataChanged.emit(self.index(0), self.index(self.rowCount()))

    def on_hists_ac(self):
        self.dataChanged.emit(self.index(0), self.index(self.rowCount()))


class ActiveListWidget(QWidget):
    def __init__(self, parent=None, *args):
        QWidget.__init__(self, parent, *args)

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

    def on_selection_changed(self):
        ids = self.list.selectionModel().selectedIndexes()
        if ids:
            idx = ids[0].row()


if __name__ == '__main__':
    import sys
    from ListWidgets.EditableListWidget import EditableListWidget
    q_app = P61BApp(sys.argv)
    app = EditableListWidget()
    app.show()
    app2 = ActiveListWidget()
    app2.show()
    sys.exit(q_app.exec())