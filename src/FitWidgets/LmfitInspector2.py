import lmfit

from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QMenu, QAction, QInputDialog, QTreeView
from PyQt5.Qt import QAbstractItemModel, Qt, QModelIndex, QVariant

from P61App import P61App
import lmfit_wrappers as lmfit_models


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

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

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

        self.beginResetModel()
        self._clear_tree()

        if self._fit_res is not None:
            for md in self._fit_res.model.components:
                self.rootItem.appendChild(TreeNode([md._name + ':' + md.prefix], self.rootItem))

                for par in self._fit_res.params:
                    if md.prefix in par:
                        self.rootItem.childItems[-1].appendChild(
                            TreeNode([
                                par,
                                '%.03E' % self._fit_res.params[par].value,
                                '± %.03E' % self._fit_res.params[par].stderr
                                if self._fit_res.params[par].stderr is not None else 'None',
                                '%.03E' % self._fit_res.params[par].min,
                                '%.03E' % self._fit_res.params[par].max,
                        ], self.rootItem.childItems[-1]))

        self.endResetModel()

    def columnCount(self, parent):
        return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            item = index.internalPointer()
            return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

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
        self.treeview_md = LmfitInspectorModel()
        self.treeview = QTreeView()
        self.treeview.setModel(self.treeview_md)

        self.menu = QMenu()

        for k in self.prefixes.keys():
            self.menu.addAction(k)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.bplus, 1, 1, 1, 1)
        layout.addWidget(self.bminus, 1, 3, 1, 1)
        layout.addWidget(self.treeview, 2, 1, 1, 3)

        self.bplus.clicked.connect(self.bplus_onclick)
        self.bminus.clicked.connect(self.bminus_onclick)

    def bplus_onclick(self):
        name = self.menu.exec(self.mapToGlobal(self.bplus.pos()))
        idx = self.q_app.get_selected_idx()

        if not isinstance(name, QAction) or idx == -1:
            return

        name = name.text()
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

        if isinstance(old_res, lmfit.model.ModelResult):
            prefixes = [md.prefix for md in old_res.model.components]
            for ii in range(100):
                if self.prefixes[name] + '%d_' % ii not in prefixes:
                    kwargs['prefix'] = self.prefixes[name] + '%d_' % ii
                    break

            new_md = getattr(lmfit_models, name)(**kwargs)
            params = old_res.params
            params.update(new_md.make_params())
            self.q_app.set_general_result(idx, lmfit.model.ModelResult(old_res.model + new_md, params))

    def bminus_onclick(self):
        pass