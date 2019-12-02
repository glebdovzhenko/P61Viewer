from PyQt5.QtWidgets import QWidget, QListWidget, QPushButton, QGridLayout
from lmfit import models as lmfit_models
from functools import reduce

from P61App import P61App


class LmfitBuilderWidget(QWidget):
    """"""

    prefixes = {'BreitWignerModel': 'bw', 'ConstantModel': 'c', 'DampedHarmonicOscillatorModel': 'dho',
                'DampedOscillatorModel': 'do', 'DonaichModel': 'don', 'ExponentialGaussianModel': 'exg',
                'ExponentialModel': 'e', 'ExpressionModel': 'expr', 'GaussianModel': 'g', 'LinearModel': 'lin',
                'LognormalModel': 'lgn', 'LorentzianModel': 'lor', 'MoffatModel': 'mof', 'ParabolicModel': 'par',
                'Pearson7Model': '7p', 'PolynomialModel': 'pol', 'PowerLawModel': 'pow', 'PseudoVoigtModel': 'pv',
                'QuadraticModel': 'qua', 'RectangleModel': 'rct', 'SkewedGaussianModel': 'sg',
                'SkewedVoigtModel': 'sv', 'SplitLorentzianModel': 'spl', 'StepModel': 'stp', 'StudentsTModel': 'st',
                'VoigtModel': 'v'}

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.model_names = [
            'PseudoVoigtModel',
            'SkewedVoigtModel',
            'ConstantModel',
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

    def update_composite_model(self, names):
        models = []
        for name in names:
            name, prefix = name.split(':')
            models.append(getattr(lmfit_models, name)(**{'name': name, 'prefix': prefix + '_'}))

        if models:
            self.q_app.params['LmFitModel'] = reduce(lambda a, b: a + b, models)
        else:
            self.q_app.params['LmFitModel'] = None

        self.q_app.data.loc[:, 'FitResult'] = None
        self.q_app.lmFitModelUpdated.emit()

    def on_btn_add(self):
        for item in self.model_selector.selectedItems():
            name = item.text()
            names = [self.model_builder.item(i).text() for i in range(self.model_builder.count())]

            for ii in range(10):
                if (name + ':' + self.prefixes[name] + str(ii)) not in names:
                    name += ':' + self.prefixes[name] + str(ii)
                    names.append(name)
                    break
            else:
                return

            self.update_composite_model(names)
            self.model_builder.addItem(name)

    def on_btn_rm(self):
        for item in self.model_builder.selectedItems():
            self.model_builder.takeItem(self.model_builder.row(item))

        names = [self.model_builder.item(i).text() for i in range(self.model_builder.count())]
        self.update_composite_model(names)


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    app = LmfitBuilderWidget()
    app.show()
    sys.exit(q_app.exec())
