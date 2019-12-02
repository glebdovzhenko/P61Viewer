from PyQt5.QtWidgets import QWidget, QTableView, QAbstractItemView, QPushButton, QCheckBox, QGridLayout, QFileDialog
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, QSize

from P61App import P61App


class LmfitInspectorModel(QAbstractTableModel):
    """

    """
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.q_app = P61App.instance()

        self.header_labels = ['Fit', 'Name', 'Value', 'STD']
        self.fit_results = None
        self.param_names = None

        self.upd_fit_results()

        self.q_app.lmFitModelUpdated.connect(self.upd_fit_results)
        self.q_app.selectedIndexChanged.connect(self.upd_fit_results)
        # TODO: this should be another function used as slot
        # self.q_app.dataFitChanged.connect(self.upd_fit_results)

    def upd_fit_results(self):
        self.beginResetModel()
        if self.q_app.params['SelectedIndex'] == -1:
            self.fit_results = None
            self.param_names = None
        else:
            self.fit_results = self.q_app.data.loc[self.q_app.params['SelectedIndex'], 'FitResult']
        if self.fit_results is not None:
            self.param_names = list(self.fit_results.params.items())
        self.endResetModel()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def rowCount(self, parent=None, *args, **kwargs):
        if self.fit_results is None:
            return 0
        else:
            return len(self.fit_results.params)

    def columnCount(self, parent=None, *args, **kwargs):
        return 4

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            if ii.column() == 1:
                return self.param_names[ii.row()][0]
            elif ii.column() == 2:
                return '%.03E' % self.fit_results.params[self.param_names[ii.row()][0]].value
            elif ii.column() == 3:
                if self.fit_results.params[self.param_names[ii.row()][0]].stderr is not None:
                    return '± %.03E' % self.fit_results.params[self.param_names[ii.row()][0]].stderr
                else:
                    return 'None'

        if role == Qt.CheckStateRole:
            if ii.column() == 0:
                return Qt.Checked if self.fit_results.params[self.param_names[ii.row()][0]].vary else Qt.Unchecked

        return QVariant()

    def flags(self, ii: QModelIndex):
        if ii.column() == 0:
            return QAbstractTableModel.flags(self, ii) | Qt.ItemIsUserCheckable
        else:
            return QAbstractTableModel.flags(self, ii)


class LmfitInspectorWidget2(QTableView):
    """

    """
    def __init__(self, parent=None):
        QTableView.__init__(self, parent)
        self.q_app = P61App.instance()

        self._model = LmfitInspectorModel()
        self.setModel(self._model)
        # self.setSelectionMode(QAbstractItemView.NoSelection)