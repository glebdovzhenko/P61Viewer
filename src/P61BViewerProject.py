from NexusHistogram import NexusHistogram
from PyQt5.QtCore import QObject, pyqtSignal
import os
from lmfit.models import GaussianModel
from functools import reduce


class P61BViewerProject(QObject):
    color_cycle = ('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf')
    prefixes = {'BreitWignerModel': 'bw', 'ConstantModel': 'c', 'DampedHarmonicOscillatorModel': 'dho',
                'DampedOscillatorModel': 'do', 'DonaichModel': 'don', 'ExponentialGaussianModel': 'exg',
                'ExponentialModel': 'e', 'ExpressionModel': 'expr', 'GaussianModel': 'g', 'LinearModel': 'lin',
                'LognormalModel': 'lgn', 'LorentzianModel': 'lor', 'MoffatModel': 'mof', 'ParabolicModel': 'par',
                'Pearson7Model': '7p', 'PolynomialModel': 'poly', 'PowerLawModel': 'pow', 'PseudoVoigtModel': 'pv',
                'QuadraticModel': 'quad', 'RectangleModel': 'rect', 'SkewedGaussianModel': 'sg',
                'SkewedVoigtModel': 'sv', 'SplitLorentzianModel': 'spl', 'StepModel': 'stp', 'StudentsTModel': 'st',
                'VoigtModel': 'v'}

    histsAdded = pyqtSignal()
    histsRemoved = pyqtSignal()
    histsActiveChanged = pyqtSignal()
    selectedHistChanged = pyqtSignal()
    plotLimUpdated = pyqtSignal()
    compositeModelUpdated = pyqtSignal()

    def __init__(self):
        QObject.__init__(self, parent=None)
        self._histograms = []
        self._active_hs = []
        self._lmfit_models = []
        self._lmfit_composite_model = GaussianModel()
        self._color_count = 0
        self.selected_id = 0
        self._plot_xlim = (0, 1)
        self._plot_ylim = (0, 1)

    def set_plot_xlim(self, val):
        self._plot_xlim = val
        self.plotLimUpdated.emit()

    def get_plot_xlim(self):
        return self._plot_xlim

    def set_plot_ylim(self, val):
        self._plot_ylim = val
        self.plotLimUpdated.emit()

    def get_plot_ylim(self):
        return self._plot_ylim

    plot_xlim = property(fget=get_plot_xlim, fset=set_plot_xlim)
    plot_ylim = property(fget=get_plot_ylim, fset=set_plot_ylim)

    def get_histogram(self, idx: int) -> NexusHistogram:
        return self._histograms[idx]

    def get_active_histogram(self, idx: int) -> NexusHistogram:
        return self._active_hs[idx]

    def set_selected_id(self, idx: int):
        if 0 <= idx < self.histogram_list_len(active=True):
            self.selected_id = idx
            self.selectedHistChanged.emit()

    def get_selected_hist(self):
        if 0 <= self.selected_id < self.histogram_list_len(active=True):
            return self.get_active_histogram(self.selected_id)

    def _update_active(self):
        self._active_hs = [h for h in self._histograms if h.active]

    def histogram_list_len(self, active=False) -> int:
        if active:
            return len(self._active_hs)
        else:
            return len(self._histograms)

    def del_histograms(self, r1, r2):
        del self._histograms[r1:r2]
        self._update_active()

    def remove_histograms(self, ids):
        ids = [idx for idx in ids if 0 <= idx < len(self._histograms)]
        for ii in sorted(ids, reverse=True):
            del self._histograms[ii]
        self._update_active()
        self.histsRemoved.emit()

    def insert_histograms(self, row, count):
        self._histograms = self._histograms[:row] + [NexusHistogram() for _ in range(count)] + self._histograms[row:]
        self._update_active()

    def get_hist_ids(self):
        return [x.dataset_id for x in self._histograms]

    def get_plot_lines(self):
        return [x.plot_line for x in self._histograms if x.active]

    def _next_color(self):
        self._color_count += 1
        return self.color_cycle[self._color_count % len(self.color_cycle)]

    def get_active_status(self, ids):
        ids = [idx for idx in ids if 0 <= idx < len(self._histograms)]
        return [self._histograms[idx].active for idx in ids]

    def set_active_status(self, ids, value):
        ids = [idx for idx in ids if 0 <= idx < len(self._histograms)]
        for idx in ids:
            self._histograms[idx].active = bool(value)
        self._update_active()
        self.histsActiveChanged.emit()

    def init_new_hists(self, f_list):
        ids = self.get_hist_ids()
        ch0, ch1 = 'entry/instrument/xspress3/channel00/histogram', \
                   'entry/instrument/xspress3/channel01/histogram'

        failed = []
        for ff in f_list:
            if (ff + ':' + ch0) not in ids:
                tmp0 = NexusHistogram()
                if tmp0.fill(ff, ch0, os.path.basename(ff) + ':ch0'):
                    tmp0.plot_color_mpl = self._next_color()
                    self._histograms.append(tmp0)
                else:
                    failed.append(ff)

            if (ff + ':' + ch1) not in ids:
                tmp1 = NexusHistogram()
                if tmp1.fill(ff, ch1, os.path.basename(ff) + ':ch1'):
                    tmp1.plot_color_mpl = self._next_color()
                    self._histograms.append(tmp1)
                else:
                    failed.append(ff)

        self._update_active()
        self.histsAdded.emit()
        return failed

    @property
    def lmfit_model_names(self):
        return [md.name for md in self._lmfit_models]

    @property
    def lmfit_composite_model(self):
        return self._lmfit_composite_model

    def lmfit_models_len(self):
        return len(self._lmfit_models)

    def get_lmfit_model(self, idx):
        return self._lmfit_models[idx]

    def remove_lmfit_model(self, idx):
        if 0 <= idx < len(self._lmfit_models):
            del self._lmfit_models[idx]
            self._lmfit_composite_model = reduce(lambda a, b: a + b, self._lmfit_models)
            self.compositeModelUpdated.emit()

    def append_lmfit_model(self, md):
        for ii in range(1, 11):
            md.prefix = self.prefixes[md._name] + '%d_' % ii
            if md.name not in self.lmfit_model_names:
                self._lmfit_models.append(md)
                self._lmfit_composite_model = reduce(lambda a, b: a + b, self._lmfit_models)
                self.compositeModelUpdated.emit()
                return True
        return False