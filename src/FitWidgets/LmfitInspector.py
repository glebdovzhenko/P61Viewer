import lmfit
import numpy as np
from copy import deepcopy
import logging
import json

from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QMenu, QAction, QInputDialog, QTreeView, \
    QStyledItemDelegate, QStyleOptionViewItem, QHeaderView, QFileDialog, QCheckBox
from PyQt5.Qt import QAbstractItemModel, Qt, QModelIndex, QVariant

from FitWidgets.FloatEdit import FloatEdit
from FitWidgets.InitPopUp import InitPopUp
from P61App import P61App
import lmfit_utils


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
        self.logger = logging.getLogger(str(self.__class__))

        self.rootItem = TreeNode(('Name', 'Value', 'STD', 'Min', 'Max'))
        self._fit_res = None
        self._upd()

        self.q_app.selectedIndexChanged.connect(self.on_selected_idx_ch)
        self.q_app.dataSorted.connect(self.on_data_sorted)
        self.q_app.genFitResChanged.connect(self.on_gen_fit_res_changed)

    def on_data_sorted(self):
        self.logger.debug('on_data_sorted: Handling dataSorted')
        self._upd()

    def on_selected_idx_ch(self, idx):
        self.logger.debug('on_selected_idx_ch: Handling selectedIndexChanged(%d)' % idx)
        self._upd()

    def on_gen_fit_res_changed(self, ids):
        self.logger.debug('on_gen_fit_res_changed: Handling genFitResChanged(%s)' % str(ids))
        self._upd()

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
            # for md in self._fit_res.model.components:
            for md in lmfit_utils.sort_components(self._fit_res):
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

        data = index.internalPointer().itemData

        if role == Qt.DisplayRole:
            if isinstance(data, lmfit.Parameter):
                data = (data.name, '%.03E' % data.value, '± %.03E' % data.stderr
                        if data.stderr is not None else 'None', '%.03E' % data.min, '%.03E' % data.max)
            elif isinstance(data, lmfit.Model):
                if ('GaussianModel' in data.name) or ('LorentzianModel' in data.name) or \
                        ('PseudoVoigtModel' in data.name):
                    center = '%.1f: ' % self._fit_res.params[data.prefix + 'center'].value
                else:
                    center = ''
                data = (center + data.prefix + ' (' + data._name + ')', ) + ('', ) * 4
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
                if result.params[data.name].min > value:
                    result.params[data.name].set(min=value)
                if result.params[data.name].max < value:
                    result.params[data.name].set(max=value)

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
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.q_app = P61App.instance()
        self.logger = logging.getLogger(str(self.__class__))

        self.bplus = QPushButton('+')
        self.bminus = QPushButton('-')
        self.bopen = QPushButton('Open')
        self.bsave = QPushButton('Save')
        self.b_from_peaklist = QPushButton('Init from PT')
        self.treeview_md = LmfitInspectorModel()
        self._delegate = SpinBoxDelegate()
        self.treeview = QTreeView()
        self.treeview.setModel(self.treeview_md)
        self.treeview.setItemDelegate(self._delegate)
        self.treeview.expandAll()
        self.treeview.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.treeview.header().setStretchLastSection(True)

        self.menu = QMenu()

        for k in lmfit_utils.prefixes.keys():
            self.menu.addAction(k)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.b_from_peaklist, 1, 1, 1, 1)
        layout.addWidget(self.bplus, 2, 1, 1, 1)
        layout.addWidget(self.bminus, 2, 3, 1, 1)
        layout.addWidget(self.bopen, 1, 2, 1, 1)
        layout.addWidget(self.bsave, 1, 3, 1, 1)
        layout.addWidget(self.treeview, 3, 1, 1, 3)

        self.bplus.clicked.connect(self.bplus_onclick)
        self.bminus.clicked.connect(self.bminus_onclick)
        self.bopen.clicked.connect(self.bopen_onclick)
        self.bsave.clicked.connect(self.bsave_onclick)
        self.b_from_peaklist.clicked.connect(self.from_peaklist_onclick)
        self.treeview_md.modelReset.connect(self.expander)

    def bopen_onclick(self):
        idx = self.q_app.get_selected_idx()
        if idx == -1:
            return

        file, _ = QFileDialog.getOpenFileName(self, "Open lmfit model",  "",
                                              "lmfit.ModelResult (*.mr);;All Files (*)")
        try:
            with open(file, 'r') as f:
                result = lmfit_utils.deserialize_model_result(json.load(f))
        except Exception as e:
            self.logger.error('bopen_onclick: during opening of %s an exception was raised: %s' % (file, str(e)))
            return

        if isinstance(result, lmfit.model.ModelResult):
            self.q_app.set_general_result(idx, result)

    def bsave_onclick(self):
        f_name, _ = QFileDialog.getSaveFileName(self, "Save fit model", "",
                                                "lmfit.ModelResult (*.mr);;All Files (*)")
        if not f_name:
            return

        idx = self.q_app.get_selected_idx()
        if idx == -1:
            return

        result = self.q_app.get_general_result(idx)
        if result is None:
            return

        with open(f_name, 'w') as f:
            json.dump(lmfit_utils.serialize_model_result(result), f)

    def from_peaklist_onclick(self):
        w = InitPopUp(parent=self)
        w.exec_()

    def init_from_peaklist(self, idx=-1):
        if idx == -1:
            idx = self.q_app.get_selected_idx()

        if idx == -1:
            return

        peak_list = self.q_app.data.loc[idx, 'PeakList']
        if peak_list is None:
            return

        present_peaks = []
        for ta in peak_list:
            for peak in ta['peaks']:
                present_peaks.append(peak['center_x'])

        self.q_app.set_general_result(idx, None)
        self._add_model('PolynomialModel', idx, {'c0': 0., 'c1': 0., 'c2': 0.})

        old_res = self.q_app.get_general_result(idx)

        # result = lmfit_utils.add_peak_md('PseudoVoigtModel', peak_list, old_res)

        stacked_list = self.q_app.stacked_peaks
        stacked_peaks = []
        if stacked_list is not None:
            for ta in self.q_app.stacked_peaks:
                stacked_peaks.extend(deepcopy(ta['peaks']))

        for pp in present_peaks:
            stacked_peaks.remove(min(stacked_peaks, key=lambda x: np.abs(x['center_x'] - pp)))

        for peak in stacked_peaks:
            peak['center_y'] = 0.1

        for ta in peak_list:
            stacked_peaks.extend(ta['peaks'])

        stacked_peaks = list(sorted(stacked_peaks, key=lambda x: x['center_x']))

        result = lmfit_utils.add_peak_md('PseudoVoigtModel', [{'peaks': stacked_peaks}], old_res)

        self.q_app.set_general_result(idx, result)

    def expander(self, *args, **kwargs):
        self.treeview.expandAll()

    def bplus_onclick(self):
        name = self.menu.exec(self.mapToGlobal(self.bplus.pos()))
        idx = self.q_app.get_selected_idx()

        if not isinstance(name, QAction) or idx == -1:
            return

        self._add_model(name.text(), idx, poly_deg_default=False)

    def bminus_onclick(self):
        selected_obj = self.treeview.currentIndex().internalPointer()
        if selected_obj is None:
            return

        if isinstance(selected_obj.itemData, lmfit.Model):
            prefix = selected_obj.itemData.prefix
            result = lmfit_utils.rm_md(prefix, self.q_app.get_general_result(self.q_app.get_selected_idx()))
            self.q_app.set_general_result(self.q_app.get_selected_idx(), result)

    def _add_model(self, name, idx, init_params=dict(), poly_deg_default=4):
        old_res = self.q_app.get_general_result(idx)

        if name == 'PolynomialModel':
            if not poly_deg_default:
                ii, ok = QInputDialog.getInt(self, 'Polynomial degree', 'Polynomial degree', 3, 2, 7, 1)
                if ok:
                    init_params['degree'] = ii
            else:
                init_params['degree'] = poly_deg_default

            for i in range(init_params['degree'] + 1):
                init_params['c%d' % i] = 0.

        result = lmfit_utils.add_md(name, init_params, old_res)
        self.q_app.set_general_result(idx, result)
