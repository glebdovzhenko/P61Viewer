import lmfit

from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QMenu, QAction, QInputDialog, QTreeView, \
    QStyledItemDelegate, QStyleOptionViewItem
from PyQt5.Qt import QAbstractItemModel, Qt, QModelIndex, QVariant

from FitWidgets.FloatEdit import FloatEdit
from P61App import P61App
import lmfit_wrappers as lmfit_models
from functools import reduce


class TreeNode(object):
    """"""
    def __init__(self, data, parent=None, lvl=0):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0


class LmfitInspectorModel(QAbstractItemModel):
    """"""

    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self.q_app = P61App.instance()

        self.rootItem = TreeNode(('Name', 'Value', 'STD', 'Min', 'Max'))
        self._fit_res = None
        self._upd()

        self.q_app.selectedIndexChanged.connect(self._upd)
        self.q_app.genFitResChanged.connect(self._upd)

    def _clear_tree(self):
        for item in self.rootItem.childItems:
            del item.childItems[:]
        del self.rootItem.childItems[:]

    def _upd(self, *args, **kwargs):
        idx = self.q_app.get_selected_idx()
        if idx == -1:
            self._fit_res = None
        else:
            self._fit_res = self.q_app.get_general_result(idx)

        self.modelAboutToBeReset.emit()  # so this is private apparently so look for a different way???
        self._clear_tree()

        if self._fit_res is not None:
            for md in self._fit_res.model.components:
                self.rootItem.appendChild(TreeNode(md, self.rootItem))

                for par in self._fit_res.params:
                    if md.prefix in par:
                        self.rootItem.childItems[-1].appendChild(
                            TreeNode(self._fit_res.params[par], self.rootItem.childItems[-1]))

        self.endResetModel()
        self.layoutChanged.emit()

    def columnCount(self, parent):
        return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()
        data = item.itemData

        if role == Qt.DisplayRole:
            if isinstance(data, lmfit.Parameter):
                data = (data.name, '%.03E' % data.value, '± %.03E' % data.stderr
                        if data.stderr is not None else 'None', '%.03E' % data.min, '%.03E' % data.max)
            elif isinstance(data, lmfit.Model):
                data = (':'.join((data._name, data.prefix)), ) + ('', ) * 4
            return data[index.column()]
        elif role == Qt.CheckStateRole:
            if index.column() == 0 and isinstance(data, lmfit.Parameter):
                if data.expr is None:
                    return Qt.Checked if data.vary else Qt.Unchecked
        elif role == Qt.EditRole:
            if isinstance(data, lmfit.Parameter):
                data = (data.name, '%.03E' % data.value, '± %.03E' % data.stderr
                        if data.stderr is not None else 'None', '%.03E' % data.min, '%.03E' % data.max)
                return data[index.column()]

        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        if index.column() == 0:
            return QAbstractItemModel.flags(self, index) | Qt.ItemIsUserCheckable
        elif index.column() in (1, 3, 4) and isinstance(index.internalPointer().itemData, lmfit.Parameter):
            return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable
        else:
            return QAbstractItemModel.flags(self, index)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.itemData[section]

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setData(self, ii: QModelIndex, value, role=None):
        if not ii.isValid():
            return False

        item = ii.internalPointer()
        data = item.itemData
        result = self.q_app.get_general_result(self.q_app.get_selected_idx())

        if role == Qt.CheckStateRole and ii.column() == 0:
            result.params[data.name].set(vary=bool(value))
            self.q_app.set_general_result(self.q_app.get_selected_idx(), result)
            return True
        elif role == Qt.EditRole:
            if ii.column() == 1:
                result.params[data.name].set(value=value)
                self.q_app.set_general_result(self.q_app.get_selected_idx(), result)
                return True
            elif ii.column() == 3:
                result.params[data.name].set(min=value)
                self.q_app.set_general_result(self.q_app.get_selected_idx(), result)
                return True
            elif ii.column() == 4:
                result.params[data.name].set(max=value)
                self.q_app.set_general_result(self.q_app.get_selected_idx(), result)
                return True

        return False


class SpinBoxDelegate(QStyledItemDelegate):
    """

    """
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, w: QWidget, s: QStyleOptionViewItem, ii: QModelIndex):
        editor = FloatEdit(parent=w)
        return editor

    def setEditorData(self, w: QWidget, ii: QModelIndex):
        w.value = float(ii.model().data(ii, Qt.EditRole))

    def setModelData(self, w: QWidget, model: QAbstractItemModel, ii: QModelIndex):
        model.setData(ii, w.value, Qt.EditRole)

    def updateEditorGeometry(self, w: QWidget, s: QStyleOptionViewItem, ii: QModelIndex):
        w.setGeometry(s.rect)


class LmfitInspector(QWidget):
    """

    """
    prefixes = {'GaussianModel': 'g', 'LorentzianModel': 'lor', 'Pearson7Model': 'pvii', 'PolynomialModel': 'pol',
                'PseudoVoigtModel': 'pv', 'SkewedGaussianModel': 'sg', 'SkewedVoigtModel': 'sv',
                'SplitLorentzianModel': 'spl'}

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.q_app = P61App.instance()

        self.bplus = QPushButton('+')
        self.bminus = QPushButton('-')
        self.b_from_peaklist = QPushButton('Init from PT')
        self.treeview_md = LmfitInspectorModel()
        self._delegate = SpinBoxDelegate()
        self.treeview = QTreeView()
        self.treeview.setModel(self.treeview_md)
        self.treeview.setItemDelegate(self._delegate)
        self.treeview.expandAll()

        self.menu = QMenu()

        for k in self.prefixes.keys():
            self.menu.addAction(k)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.b_from_peaklist, 1, 1, 1, 1)
        layout.addWidget(self.bplus, 2, 1, 1, 1)
        layout.addWidget(self.bminus, 2, 3, 1, 1)
        layout.addWidget(self.treeview, 3, 1, 1, 3)

        self.bplus.clicked.connect(self.bplus_onclick)
        self.bminus.clicked.connect(self.bminus_onclick)
        self.b_from_peaklist.clicked.connect(self.from_peaklist_onclick)
        self.treeview_md.modelReset.connect(self.expander)

    def from_peaklist_onclick(self):
        print('Clickl')

    def expander(self, *args, **kwargs):
        self.treeview.expandAll()

    def bplus_onclick(self):
        name = self.menu.exec(self.mapToGlobal(self.bplus.pos()))
        idx = self.q_app.get_selected_idx()

        if not isinstance(name, QAction) or idx == -1:
            return

        self._add_model(name.text(), idx)

    def bminus_onclick(self):
        selected_obj = self.treeview.currentIndex().internalPointer()
        if selected_obj is None:
            return

        if isinstance(selected_obj.itemData, lmfit.Model):
            prefix = selected_obj.itemData.prefix
            result = self.q_app.get_general_result(self.q_app.get_selected_idx())

            if len(result.model.components) == 1:
                self.q_app.set_general_result(self.q_app.get_selected_idx(), None)
                return

            new_md = reduce(lambda a, b: a + b, (cmp for cmp in result.model.components if cmp.prefix != prefix))
            new_params = result.params.copy()
            for par in result.params:
                if prefix in result.params[par].name:
                    new_params.pop(par)

            result.model = new_md
            result.params = new_params
            self.q_app.set_general_result(self.q_app.get_selected_idx(), result)

    def _add_model(self, name, idx):
        old_res = self.q_app.get_general_result(idx)

        kwargs = {'name': name}
        if name == 'PolynomialModel':
            ii, ok = QInputDialog.getInt(self, 'Polynomial degree', 'Polynomial degree', 3, 2, 7, 1)
            if ok:
                kwargs['degree'] = ii

        if old_res is None:
            kwargs['prefix'] = self.prefixes[name] + '0_'
            new_md = getattr(lmfit_models, name)(**kwargs)
            self.q_app.set_general_result(idx, lmfit.model.ModelResult(new_md, new_md.make_params()))
        elif isinstance(old_res, lmfit.model.ModelResult):
            prefixes = [md.prefix for md in old_res.model.components]
            for ii in range(100):
                if self.prefixes[name] + '%d_' % ii not in prefixes:
                    kwargs['prefix'] = self.prefixes[name] + '%d_' % ii
                    break

            new_md = getattr(lmfit_models, name)(**kwargs)
            params = old_res.params
            params.update(new_md.make_params())
            self.q_app.set_general_result(idx, lmfit.model.ModelResult(old_res.model + new_md, params))
