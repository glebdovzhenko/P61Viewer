import lmfit

from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QMenu, QAction, QInputDialog, QTreeView
from PyQt5.Qt import QStandardItemModel, Qt, QModelIndex, QVariant

from P61App import P61App
import lmfit_wrappers as lmfit_models


class LmfitInspectorModel(QStandardItemModel):
    """"""

    def __init__(self, parent=None):
        QStandardItemModel.__init__(self, parent)
        self.q_app = P61App.instance()

        self.header_labels = ['Name', 'Value', 'STD', 'Min', 'Max']
        self._fit_res = None
        self._upd()

        self.q_app.selectedIndexChanged.connect(self._upd)
        self.q_app.genFitResChanged.connect(self._upd)

    def _upd(self, *args, **kwargs):
        self.beginResetModel()
        idx = self.q_app.get_selected_idx()
        if idx == -1:
            self._fit_res = None
        else:
            self._fit_res = self.q_app.get_general_result(idx)
        self.endResetModel()


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