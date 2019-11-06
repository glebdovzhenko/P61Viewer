from PyQt5.QtWidgets import QWidget, QListWidget, QGridLayout, QLabel, QPushButton, QListView, QInputDialog
from PyQt5.QtCore import QAbstractListModel, QModelIndex, QVariant, Qt
from lmfit import models as lmfit_models
from functools import reduce
from lmfit import Model
import inspect

from P61BApp import P61BApp


class FitModelBuilderModel(QAbstractListModel):

    prefixes = {'BreitWignerModel': 'bw', 'ConstantModel': 'c', 'DampedHarmonicOscillatorModel': 'dho',
                'DampedOscillatorModel': 'do', 'DonaichModel': 'don', 'ExponentialGaussianModel': 'exg',
                'ExponentialModel': 'e', 'ExpressionModel': 'expr', 'GaussianModel': 'g', 'LinearModel': 'lin',
                'LognormalModel': 'lgn', 'LorentzianModel': 'lor', 'MoffatModel': 'mof', 'ParabolicModel': 'par',
                'Pearson7Model': '7p', 'PolynomialModel': 'pol', 'PowerLawModel': 'pow', 'PseudoVoigtModel': 'pv',
                'QuadraticModel': 'qua', 'RectangleModel': 'rct', 'SkewedGaussianModel': 'sg',
                'SkewedVoigtModel': 'sv', 'SplitLorentzianModel': 'spl', 'StepModel': 'stp', 'StudentsTModel': 'st',
                'VoigtModel': 'v'}

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent=parent)
        self.q_app = P61BApp.instance()

        self._model_list = []

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._model_list)

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            md = self._model_list[ii.row()]
            return QVariant(md._name + ':' + md.prefix)

    def remove_row_by_idx(self, idx):
        self.beginRemoveRows(idx, idx.row(), idx.row())
        del self._model_list[idx.row()]
        self.endRemoveRows()

    def append_row(self, model_name, **kwargs):
        kwargs.update({'name': model_name})
        prefixes = [md.prefix for md in self._model_list]
        for ii in range(10):
            prx = self.prefixes[model_name] + str(ii) + '_'
            if prx not in prefixes:
                kwargs.update({'prefix': prx})
                break

        new_model = getattr(lmfit_models, model_name)(**kwargs)
        self.beginInsertRows(self.index(self.rowCount()), self.rowCount(), self.rowCount() + 1)
        self._model_list.append(new_model)
        self.endInsertRows()

    def set_composite(self):
        if self._model_list:
            self.q_app.params['LmFitModel'] = reduce(lambda a, b: a + b, self._model_list)
            self.q_app.lmFitModelUpdated.emit()
        else:
            self.q_app.params['LmFitModel'] = None
            self.q_app.lmFitModelUpdated.emit()
        self.q_app.data.loc[:, 'FitResult'] = None


class FitModelBuilderWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61BApp.instance()

        # special cases: ExpressionModel and PolynomialModel
        # self.model_names = []
        # for k in dir(lmfit_models):
        #     if inspect.isclass(getattr(lmfit_models, k)):
        #         if issubclass(getattr(lmfit_models, k), Model):
        #             self.model_names.append(k)
        # self.model_names.remove('Model')
        # self.model_names.remove('ExpressionModel')
        # self.model_names.remove('ComplexConstantModel')
        self.model_names = ['PseudoVoigtModel', 'SkewedVoigtModel', 'ConstantModel', 'LinearModel',  'PolynomialModel']

        self.label = QLabel('Build your model by adding elements to the right:', parent=self)
        self.lmfit_selector = QListWidget(parent=self)
        self.lmfit_builder = QListView(parent=self)
        self.lmfit_builder_md = FitModelBuilderModel()
        self.lmfit_builder.setModel(self.lmfit_builder_md)
        self.lmfit_selector.addItems(self.model_names)

        self.lmfit_selector.setFixedWidth(150)
        self.lmfit_selector.setFixedHeight(100)
        self.lmfit_builder.setFixedWidth(150)
        self.lmfit_builder.setFixedHeight(100)

        self.btn_add = QPushButton('>', parent=self)
        self.btn_rm = QPushButton('<', parent=self)
        self.btn_add.clicked.connect(self.on_btn_add)
        self.btn_rm.clicked.connect(self.on_btn_rm)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.label, 1, 1, 1, 3)
        layout.addWidget(self.lmfit_selector, 2, 1, 4, 1)
        layout.addWidget(self.lmfit_builder, 2, 3, 4, 1)
        layout.addWidget(self.btn_add, 3, 2, 1, 1)
        layout.addWidget(self.btn_rm, 4, 2, 1, 1)

    def on_btn_add(self):
        if self.lmfit_selector.selectedItems():
            model_name = self.lmfit_selector.selectedItems()[0].text()
            if model_name == 'PolynomialModel':
                item, ok = QInputDialog.getItem(self, 'PolynomialModel', 'Polynomial degree',
                                                ('3', '4', '5', '6', '7'), 0, False)
                if ok and item:
                    self.lmfit_builder_md.append_row(model_name, degree=int(item))
            elif model_name == 'ExpressionModel':
                pass
            else:
                self.lmfit_builder_md.append_row(model_name)
        self.lmfit_builder_md.set_composite()

    def on_btn_rm(self):
        if self.lmfit_builder.selectedIndexes():
            self.lmfit_builder_md.remove_row_by_idx(self.lmfit_builder.selectedIndexes()[0])
            self.lmfit_builder.clearSelection()
        self.lmfit_builder_md.set_composite()


if __name__ == '__main__':
    import sys
    q_app = P61BApp(sys.argv)
    app = FitModelBuilderWidget()
    app.show()
    sys.exit(q_app.exec())