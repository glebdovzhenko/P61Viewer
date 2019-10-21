from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant, QSize
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QListView, QAbstractItemView, QPushButton, QCheckBox, QGridLayout, QFileDialog, \
    QErrorMessage

from P61BApp import P61BApp


class EditableListModel(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)

    def rowCount(self, parent=None, *args, **kwargs):
        return P61BApp.instance().project.histogram_list_len()

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return QVariant()

        row = ii.row()

        if role == Qt.DisplayRole:
            return QVariant(P61BApp.instance().project.get_histogram(row).name)
        elif role == Qt.ForegroundRole:
            if P61BApp.instance().project.get_histogram(row).active:
                return QColor(*P61BApp.instance().project.get_histogram(row).plot_color_qt, 255)
            else:
                return QColor(0, 0, 0, 255)
        elif role == Qt.CheckStateRole:
            return Qt.Checked if P61BApp.instance().project.get_histogram(row).active else Qt.Unchecked

    def setData(self, ii: QModelIndex, value, role=None):
        if not ii.isValid():
            return False

        if role == Qt.CheckStateRole:
            P61BApp.instance().project.set_active_status([ii.row()], value)
            self.dataChanged.emit(ii, ii)
            return True
        return False

    def flags(self, index: QModelIndex) -> QVariant:
        return QAbstractListModel.flags(self, index) | Qt.ItemIsUserCheckable

    def append_rows_from_fs(self, fs):
        if not fs:
            return []

        max_idx = self.index(self.rowCount())
        self.beginInsertRows(max_idx, self.rowCount(), self.rowCount() + len(fs))
        failed = P61BApp.instance().project.init_new_hists(fs)
        self.endInsertRows()
        # self.dataChanged.emit(max_idx, self.index(self.rowCount()))
        return failed

    def remove_rows_by_idx(self, ids):
        ids = [idx for idx in ids if idx.isValid()]
        if not ids:
            return

        rows = [idx.row() for idx in ids]
        self.beginRemoveRows(min(ids), min(rows), max(rows))
        P61BApp.instance().project.remove_histograms(rows)
        self.endRemoveRows()
        ids = [idx for idx in ids if idx.isValid()]
        self.dataChanged.emit(min(ids), max(ids))

    def set_active_status(self, ids, value):
        ids = [idx for idx in ids if idx.isValid()]
        if not ids:
            return
        rows = [idx.row() for idx in ids]
        P61BApp.instance().project.set_active_status(rows, value)
        self.dataChanged.emit(min(ids), max(ids))

    def get_active_status(self, ids):
        ids = [idx for idx in ids if idx.isValid()]
        if not ids:
            return []
        rows = [idx.row() for idx in ids]
        return P61BApp.instance().project.get_active_status(rows)


class EditableListWidget(QWidget):
    def __init__(self, parent=None, *args):
        QWidget.__init__(self, parent, *args)

        # list
        self._model = EditableListModel()
        self.list = QListView()
        self.list.setModel(self._model)
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # buttons and checkbox
        self.bplus = QPushButton('+')
        self.bminus = QPushButton('-')
        self.check_box = QCheckBox(' ')
        self.check_box.setTristate(False)
        self.bplus.setFixedSize(QSize(51, 32))
        self.bminus.setFixedSize(QSize(51, 32))
        self.bplus.clicked.connect(self.bplus_onclick)
        self.bminus.clicked.connect(self.bminus_onclick)
        self.check_box.clicked.connect(self.check_box_on_click)

        # layouts
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.check_box, 1, 1, 1, 1)
        layout.addWidget(self.bplus, 1, 3, 1, 1)
        layout.addWidget(self.bminus, 1, 4, 1, 1)
        layout.addWidget(self.list, 2, 1, 1, 4)

        # signal handlers
        self.list.selectionModel().selectionChanged.connect(self.check_box_update)
        self._model.dataChanged.connect(self.check_box_update)

    def bminus_onclick(self):
        self._model.remove_rows_by_idx(self.list.selectedIndexes())

    def bplus_onclick(self):
        fd = QFileDialog()
        files, _ = fd.getOpenFileNames(self,
            'Add spectra',
            '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/pwdr_h5',
            'All Files (*);;NEXUS files (*.nxs)',
            options=QFileDialog.Options()
        )

        failed = self._model.append_rows_from_fs(files)

        if failed:
            msg = QErrorMessage()
            msg.showMessage('Could not open files:\n' + '\n'.join(failed))
            msg.exec_()

    def check_box_on_click(self):
        self.check_box.setTristate(False)
        self._model.set_active_status(self.list.selectionModel().selectedIndexes(), self.check_box.checkState())

    def check_box_update(self):
        status = self._model.get_active_status(self.list.selectionModel().selectedIndexes())

        if all(status):
            self.check_box.setCheckState(Qt.Checked)
        elif not any(status):
            self.check_box.setCheckState(Qt.Unchecked)
        else:
            self.check_box.setCheckState(Qt.PartiallyChecked)


if __name__ == '__main__':
    import sys
    q_app = P61BApp(sys.argv)
    app = EditableListWidget()
    app.show()
    sys.exit(q_app.exec_())
