import numpy as np

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, QItemSelectionModel, pyqtSlot
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QTableView, QAbstractItemView, QGridLayout, QHeaderView

from P61App import P61App


class FitFileTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.q_app = P61App.instance()

        self._data = None
        self._upd()

        # signals
        self.q_app.dataRowsAppended.connect(self._upd)
        self.q_app.dataRowsRemoved.connect(self._upd)
        self.q_app.dataActiveChanged.connect(self._upd)
        self.q_app.genFitResChanged.connect(self._upd)

    @staticmethod
    def _set_chisq(row):
        if row['GeneralFitResult'] is not None:
            row['Chisqr'] = row['GeneralFitResult'].chisqr
        else:
            row['Chisqr'] = np.NaN
        return row

    def _upd(self, *args, **kwargs):
        self.beginResetModel()
        self._data = self.q_app.data.loc[self.q_app.data['Active'], ['ScreenName', 'Color', 'GeneralFitResult']]
        self._data = self._data.apply(self._set_chisq, axis=1)
        self.endResetModel()

    def rowCount(self, parent=None, *args, **kwargs):
        return self._data.shape[0]

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ['File', u'χ²'][section]
        return None

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return QVariant()

        if ii.column() == 0:
            if role == Qt.DisplayRole:
                return self._data['ScreenName'].iloc[ii.row()]
            elif role == Qt.ForegroundRole:
                return QColor(self._data['Color'].iloc[ii.row()])
        elif ii.column() == 1:
            if role == Qt.DisplayRole:
                chisqr = self._data['Chisqr'].iloc[ii.row()]
                return ('%.01f' % chisqr) if not np.isnan(chisqr) else ''
            elif role == Qt.ForegroundRole:
                return QColor('Grey')

    def get_indices(self):
        return self._data.index


class FitFileTableView(QTableView):
    def __init__(self, parent=None):
        QTableView.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)

    @pyqtSlot()
    def dataChanged(self, topLeft, bottomRight, roles):
        QTableView.dataChanged(self, topLeft, bottomRight, roles)
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


class FitFileTable(QWidget):
    def __init__(self, parent=None, *args):
        QWidget.__init__(self, parent, *args)
        self.q_app = P61App.instance()

        # list
        self._model = FitFileTableModel()
        self.list = FitFileTableView()
        self.list.setModel(self._model)
        self.list.selectionModel().selectionChanged.connect(self.list.update_selection_model)

        # layouts
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.list, 1, 1, 1, 1)

    def get_selection(self):
        ids = self.list.selectedIndexes()
        ai = self.q_app.get_active_ids()
        return [ai[idx.row()] for idx in ids]