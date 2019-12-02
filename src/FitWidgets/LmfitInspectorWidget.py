from PyQt5.QtWidgets import QTableView, QAbstractItemView, QStyledItemDelegate, QWidget, QStyleOptionViewItem
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant

from FitWidgets.FloatEditWidget import FloatEditWidget
from P61App import P61App


class LmfitInspectorModel(QAbstractTableModel):
    """

    """
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.q_app = P61App.instance()

        self.header_labels = ['Fit', 'Name', 'Value', 'STD', 'Min', 'Max']
        self.fit_results = None
        self.param_names = None

        self.upd_fit_results()

        self.q_app.lmFitModelUpdated.connect(self.upd_fit_results)
        self.q_app.selectedIndexChanged.connect(self.upd_fit_results)
        self.q_app.dataFitChanged.connect(self.upd_fit_results)

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
        return 6

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return QVariant()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if ii.column() == 1:
                return self.param_names[ii.row()][0]
            elif ii.column() == 2:
                return '%.03E' % self.fit_results.params[self.param_names[ii.row()][0]].value
            elif ii.column() == 3:
                if self.fit_results.params[self.param_names[ii.row()][0]].stderr is not None:
                    return '± %.03E' % self.fit_results.params[self.param_names[ii.row()][0]].stderr
                else:
                    return 'None'
            elif ii.column() == 4:
                return '%.03E' % self.fit_results.params[self.param_names[ii.row()][0]].min
            elif ii.column() == 5:
                return '%.03E' % self.fit_results.params[self.param_names[ii.row()][0]].max

        if role == Qt.CheckStateRole:
            if ii.column() == 0:
                return Qt.Checked if self.fit_results.params[self.param_names[ii.row()][0]].vary else Qt.Unchecked

        return QVariant()

    def setData(self, ii: QModelIndex, value, role=None):
        if not ii.isValid():
            return False

        if role == Qt.CheckStateRole and ii.column() == 0:
            self.fit_results.params[self.param_names[ii.row()][0]].vary = bool(value)
            return True

        if role == Qt.EditRole and ii.column() == 2:
            self.fit_results.params[self.param_names[ii.row()][0]].set(value=value)
            self.dataChanged.emit(ii, ii)
            self.q_app.dataFitChanged.emit(self.q_app.params['SelectedIndex'])
            return True

        if role == Qt.EditRole and ii.column() == 4:
            self.fit_results.params[self.param_names[ii.row()][0]].set(min=value)
            self.dataChanged.emit(ii, ii)
            return True

        if role == Qt.EditRole and ii.column() == 5:
            self.fit_results.params[self.param_names[ii.row()][0]].set(max=value)
            self.dataChanged.emit(ii, ii)
            return True

        return False

    def flags(self, ii: QModelIndex):
        if ii.column() == 0:
            return QAbstractTableModel.flags(self, ii) | Qt.ItemIsUserCheckable
        elif ii.column() in (2, 4, 5):
            return QAbstractTableModel.flags(self, ii) | Qt.ItemIsEditable
        else:
            return QAbstractTableModel.flags(self, ii)


class SpinBoxDelegate(QStyledItemDelegate):
    """

    """
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, w: QWidget, s: QStyleOptionViewItem, ii: QModelIndex):
        editor = FloatEditWidget(parent=w)
        return editor

    def setEditorData(self, w: QWidget, ii: QModelIndex):
        w.set_value(float(ii.model().data(ii, Qt.EditRole)), emit=False)

    def setModelData(self, w: QWidget, model: QAbstractTableModel, ii: QModelIndex):
        model.setData(ii, w.value, Qt.EditRole)

    def updateEditorGeometry(self, w: QWidget, s: QStyleOptionViewItem, ii: QModelIndex):
        w.setGeometry(s.rect)


class LmfitInspectorWidget(QTableView):
    """

    """
    def __init__(self, parent=None):
        QTableView.__init__(self, parent)
        self.q_app = P61App.instance()

        self._model = LmfitInspectorModel()
        self._delegate = SpinBoxDelegate()
        self.setModel(self._model)
        self.setItemDelegate(self._delegate)
        self.setSelectionMode(QAbstractItemView.NoSelection)