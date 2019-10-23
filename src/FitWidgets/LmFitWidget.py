from PyQt5.QtWidgets import QWidget, QListWidget, QGridLayout, QLabel, QPushButton, QListView, QInputDialog, QScrollArea, QHBoxLayout
from PyQt5.QtCore import QAbstractListModel, QModelIndex, QVariant, Qt
from lmfit import models as lmfit_models
from lmfit import Model
import inspect

from P61BApp import P61BApp
from ListWidgets import ActiveListWidget
from FitWidgets.LmFitModelWidget import LmfitModelWidget


class LmFitBuilderModel(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent=parent)

    def rowCount(self, parent=None, *args, **kwargs):
        return P61BApp.instance().project.lmfit_models_len()

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return QVariant()

        row = ii.row()

        if role == Qt.DisplayRole:
            md = P61BApp.instance().project.get_lmfit_model(row)
            return QVariant(md._name + ':' + md.prefix)

    def remove_row_by_idx(self, idx):
        self.beginRemoveRows(idx, idx.row(), idx.row())
        P61BApp.instance().project.remove_lmfit_model(idx.row())
        self.endRemoveRows()

    def append_row(self, model_name, **kwargs):
        kwargs.update({'name': model_name})
        new_model = getattr(lmfit_models, model_name)(**kwargs)

        max_idx = self.index(self.rowCount())
        self.beginInsertRows(max_idx, self.rowCount(), self.rowCount() + 1)
        failed = P61BApp.instance().project.append_lmfit_model(new_model)
        self.endInsertRows()
        # self.dataChanged.emit(max_idx, self.index(self.rowCount()))
        return failed


class LmFitWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

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
        self.list_all = QListWidget(parent=self)
        self.list_selected = QListView(parent=self)
        self.list_selected_md = LmFitBuilderModel()
        self.list_selected.setModel(self.list_selected_md)
        self.list_all.addItems(self.model_names)

        self.list_all.setFixedWidth(150)
        self.list_all.setFixedHeight(200)
        self.list_selected.setFixedWidth(150)
        self.list_selected.setFixedHeight(200)

        self.btn_add = QPushButton('>', parent=self)
        self.btn_rm = QPushButton('<', parent=self)
        self.btn_add.clicked.connect(self.on_btn_add)
        self.btn_rm.clicked.connect(self.on_btn_rm)

        self.scroll_area = QScrollArea(parent=self)
        self.lmfit_view = LmfitModelWidget(parent=self.scroll_area)
        self.scroll_area.setWidget(self.lmfit_view)

        self.active_list = ActiveListWidget()

        self.fit_btn = QPushButton('Fit this')
        self.fit_all_btn = QPushButton('Fit all')
        self.copy_btn = QPushButton('Copy params')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.label, 1, 1, 1, 3)
        layout.addWidget(self.list_all, 2, 1, 4, 1)
        layout.addWidget(self.list_selected, 2, 3, 4, 1)
        layout.addWidget(self.btn_add, 3, 2, 1, 1)
        layout.addWidget(self.btn_rm, 4, 2, 1, 1)
        layout.addWidget(self.scroll_area, 6, 1, 1, 3)
        layout.addWidget(self.active_list, 7, 2, 3, 2)
        layout.addWidget(self.fit_btn, 7, 1, 1, 1)
        layout.addWidget(self.fit_all_btn, 8, 1, 1, 1)
        layout.addWidget(self.copy_btn, 9, 1, 1, 1)

    def on_btn_add(self):
        if self.list_all.selectedItems():
            model_name = self.list_all.selectedItems()[0].text()
            if model_name == 'PolynomialModel':
                item, ok = QInputDialog.getItem(self, 'PolynomialModel', 'Polynomial degree',
                                                ('3', '4', '5', '6', '7'), 0, False)
                if ok and item:
                    self.list_selected_md.append_row(model_name, degree=int(item))
            elif model_name == 'ExpressionModel':
                pass
            else:
                self.list_selected_md.append_row(model_name)

    def on_btn_rm(self):
        if self.list_selected.selectedIndexes():
            self.list_selected_md.remove_row_by_idx(self.list_selected.selectedIndexes()[0])


if __name__ == '__main__':
    import sys
    q_app = P61BApp(sys.argv)
    app = LmFitWidget()
    app.show()
    sys.exit(q_app.exec())