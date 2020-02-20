from PyQt5.QtWidgets import QWidget, QListWidget, QPushButton, QGridLayout, QInputDialog
import lmfit_wrappers as lmfit_models
import lmfit
from functools import reduce

from P61App import P61App


class LmfitBuilderWidget(QWidget):
    """"""

    prefixes = {'BreitWignerModel': 'bw', 'ConstantModel': 'c', 'DampedHarmonicOscillatorModel': 'dho',
                'DampedOscillatorModel': 'do', 'DonaichModel': 'don', 'ExponentialGaussianModel': 'exg',
                'ExponentialModel': 'e', 'ExpressionModel': 'expr', 'GaussianModel': 'g', 'LinearModel': 'lin',
                'LognormalModel': 'lgn', 'LorentzianModel': 'lor', 'MoffatModel': 'mof', 'ParabolicModel': 'par',
                'Pearson7Model': 'pvii', 'PolynomialModel': 'pol', 'PowerLawModel': 'pow', 'PseudoVoigtModel': 'pv',
                'QuadraticModel': 'qua', 'RectangleModel': 'rct', 'SkewedGaussianModel': 'sg',
                'SkewedVoigtModel': 'sv', 'SplitLorentzianModel': 'spl', 'StepModel': 'stp', 'StudentsTModel': 'st',
                'VoigtModel': 'v'}

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.model_names = [
            'VoigtModel',
            'PseudoVoigtModel',
            'SkewedVoigtModel',
            'GaussianModel',
            'SkewedGaussianModel',
            'LorentzianModel',
            'SplitLorentzianModel',
            'Pearson7Model',
            'LinearModel',
            'PolynomialModel'
        ]

        self.model_selector = QListWidget(parent=self)
        self.model_builder = QListWidget(parent=self)
        self.btn_add = QPushButton('>', parent=self)
        self.btn_rm = QPushButton('<', parent=self)
        self.btn_add.clicked.connect(self.on_btn_add)
        self.btn_rm.clicked.connect(self.on_btn_rm)

        self.model_selector.addItems(self.model_names)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.model_selector, 1, 1, 4, 1)
        layout.addWidget(self.model_builder, 1, 3, 4, 1)
        layout.addWidget(self.btn_add, 2, 2, 1, 1)
        layout.addWidget(self.btn_rm, 3, 2, 1, 1)

    def update_composite_model(self):

        if self.q_app.params['FunctionFitModel']:
            model = reduce(lambda a, b: a + b, self.q_app.params['FunctionFitModel'].values())
        else:
            self.q_app.clear_function_fit_results()
            self.q_app.dataFitChanged.emit(self.q_app.get_all_ids().tolist())
            return

        for idx in self.q_app.get_active_ids():
            if self.q_app.get_function_fit_result(idx) is None:
                self.q_app.set_function_fit_result(
                    idx,
                    lmfit.model.ModelResult(
                        model,
                        model.make_params()),
                    emit=False)
            else:
                # new_params = model.make_params()
                new_params = reduce(lambda a, b: a + b, (cmp.make_params() for cmp in model.components))
                params = self.q_app.get_function_fit_result(idx).params
                ks1, ks2 = params.keys() & new_params.keys(), params.keys() - new_params.keys()

                for k in ks1:
                    new_params.pop(k, None)

                for k in ks2:
                    params.pop(k, None)

                params.update(new_params)

                self.q_app.set_function_fit_result(
                    idx,
                    lmfit.model.ModelResult(model, params),
                    emit=False)

        self.q_app.dataFitChanged.emit(self.q_app.get_all_ids().tolist())

    def on_btn_add(self):
        for item in self.model_selector.selectedItems():
            name = item.text()
            names = [self.model_builder.item(i).text() for i in range(self.model_builder.count())]

            for ii in range(10):
                if (name + ':' + self.prefixes[name] + str(ii)) not in names:
                    prefix = self.prefixes[name] + str(ii)
                    break
            else:
                return

            kwargs = {'name': name, 'prefix': prefix + '_'}
            if name == 'PolynomialModel':
                ii, ok = QInputDialog.getInt(self, 'Polynomial degree', '', 3, 2, 7, 1)
                if ok:
                    kwargs['degree'] = ii
                else:
                    continue
            self.q_app.params['FunctionFitModel'][name + ':' + prefix] = getattr(lmfit_models, name)(**kwargs)

            self.model_builder.addItem(name + ':' + prefix)
            self.update_composite_model()

    def on_btn_rm(self):
        for item in self.model_builder.selectedItems():
            self.model_builder.takeItem(self.model_builder.row(item))

            self.q_app.params['FunctionFitModel'].pop(item.text())
            self.update_composite_model()


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = LmfitBuilderWidget()
    app.show()
    sys.exit(q_app.exec())
