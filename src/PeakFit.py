import abc
import numpy as np
from scipy.optimize import curve_fit, OptimizeWarning


class PeakFit(metaclass=abc.ABCMeta):
    states = ('Init', 'Fail', 'Success')
    param_names = ()
    func_label = ''
    bounds = (-np.inf, np.inf)

    def __init__(self, xdata, ydata):
        self.state = self.states[0]
        self.param_values = np.array([0.0] * len(self.param_names))
        self.param_errs = np.array([np.inf] * len(self.param_names))
        self.param_use = np.array([True] * len(self.param_names))
        self.fit_err = np.inf

        self.xdata = np.array(xdata)
        self.ydata = np.array(ydata)
        self.xma, self.xmi = np.argmax(self.xdata), np.argmin(self.xdata)
        self.yma, self.ymi = np.argmax(self.ydata), np.argmin(self.ydata)

        self.guess_params()

    @abc.abstractmethod
    def guess_params(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def function(x, *args):
        pass

    @property
    def fit_ydata(self):
        return self.function(self.xdata, *self.param_values)

    @property
    def pretty_params(self):
        result = []
        for n, v, e in zip(self.param_names, self.param_values, self.param_errs):
            result.append('%s = %.2E +- %.2E' % (n, v, e))
        return ('Error: %.2E; ' % self.fit_err) + ', '.join(result)

    def guess_amplitude(self):
        return self.ydata[self.yma] - 0.5 * (self.ydata[self.xma] + self.ydata[self.xmi])

    def guess_center(self):
        return self.xdata[self.yma]

    def guess_width(self):
        return 0.1 * (self.xdata[self.xma] - self.xdata[self.xmi])

    def guess_slope(self):
        return (self.ydata[self.xma] - self.ydata[self.xmi]) / (self.xdata[self.xmi] - self.xdata[self.xma])

    def guess_intercept(self):
        return self.ydata[self.xmi] - self.param_values[3] * self.xdata[self.xmi]

    def set_param_use(self, n_val):
        if len(n_val) != len(self.param_use):
            raise ValueError()

        self.param_use[:] = list(map(bool, n_val))

    def minimize(self):
        if not any(self.param_use):
            return

        aa = np.array(self.param_values)

        def fit_fn(x, *args):
            aa[self.param_use] = args
            return self.function(x, *aa)

        try:
            popt, pcov = curve_fit(f=fit_fn, xdata=self.xdata, ydata=self.ydata, p0=self.param_values[self.param_use],
                                   bounds=(self.bounds[0][self.param_use], self.bounds[1][self.param_use]))
            self.state = self.states[2]
            self.param_values[self.param_use] = popt
            self.param_errs[self.param_use] = np.sqrt(np.diag(pcov))
        except (ValueError, OptimizeWarning) as e:
            self.state = self.states[1]
            print(e)
        self.fit_err = np.sum((self.ydata - self.fit_ydata) ** 2) / self.ydata.shape[0]


class GaussianFit(PeakFit):
    param_names = ('A', 'x0', 's', 'a', 'b')
    func_label = 'y[x] = %s * exp{-0.5 * ((x - %s) / %s) ** 2} + %s * x + %s' % param_names
    bounds = np.array(((0., -np.inf, 0., -np.inf, -np.inf),
                      (np.inf, np.inf, np.inf, np.inf, np.inf)))

    @staticmethod
    def function(x, *args):
        return args[0] * np.exp(-0.5 * ((x - args[1]) / args[2]) ** 2) + args[3] * x + args[4]

    def guess_params(self):
        self.param_errs = np.zeros(len(self.param_names))
        self.param_values = np.zeros(len(self.param_names))

        self.param_values[0] = self.guess_amplitude()
        self.param_values[1] = self.guess_center()
        self.param_values[2] = self.guess_width()
        self.param_values[3] = self.guess_slope()
        self.param_values[4] = self.guess_intercept()


class LorentzianFit(PeakFit):
    param_names = ('A', 'x0', 'g', 'a', 'b')
    func_label = 'y[x] = (%s * %s ** 2) / ((x - %s) ** 2 + %s ** 2) + %s * x + %s' % \
                 (param_names[0], param_names[2],param_names[1], param_names[2], param_names[3], param_names[4])
    bounds = np.array(((0., -np.inf, 0., -np.inf, -np.inf),
                      (np.inf, np.inf, np.inf, np.inf, np.inf)))

    @staticmethod
    def function(x, *args):
        return (args[0] * args[2] ** 2) / ((x - args[1]) ** 2 + args[2] ** 2) + args[3] * x + args[4]

    def guess_params(self):
        GaussianFit.guess_params(self)


class PsVoigtFit(PeakFit):
    param_names = ('A', 'n', 'x0', 'g', 's', 'a', 'b')
    func_label = 'y[x] = %s * (%s * exp{-0.5 * ((x - %s) / %s) ** 2} + \n' \
                 '((1 - %s) * %s ** 2) / ((x - %s) ** 2 + %s ** 2))) + %s * x + %s' \
                 % (param_names[0], param_names[1], param_names[2], param_names[4], param_names[1],
                    param_names[3], param_names[2], param_names[3], param_names[5], param_names[6])
    bounds = np.array(((0., 0, -np.inf, 0., 0., -np.inf, -np.inf),
                      (np.inf, 1., np.inf, np.inf, np.inf, np.inf, np.inf)))

    @staticmethod
    def function(x, *args):
        return args[1] * GaussianFit.function(x, args[0], args[2], args[4], 0., 0.) + \
               (1. - args[1]) * LorentzianFit.function(x, args[0], args[2], args[3], 0., 0.) + args[5] * x + args[6]

    def guess_params(self):
        self.param_errs = np.zeros(len(self.param_names))
        self.param_values = np.zeros(len(self.param_names))

        self.param_values[0] = self.guess_amplitude()
        self.param_values[1] = 0.5
        self.param_values[2] = self.guess_center()
        self.param_values[3] = self.guess_width()
        self.param_values[4] = self.guess_width()
        self.param_values[5] = self.guess_slope()
        self.param_values[6] = self.guess_intercept()


if __name__ == '__main__':
    from src.NexusHistogram import NexusHistogram
    from matplotlib import pyplot as plt
    import os

    f_name = '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/collected/' \
             'Co57_2019-09-30::09:10:30_.nxs'
    ch_name = 'entry/instrument/xspress3/channel00/histogram'

    d = NexusHistogram()
    d.fill(f_name, ch_name, os.path.basename(f_name) + ':ch0')
    d = d._dataset
    d = d[120:124]

    gf = GaussianFit(xdata=d.index, ydata=d.values)
    gf.set_param_use([0, 0, 1, 0, 0])
    gf.minimize()
    print(gf.func_label)
    print(gf.pretty_params)

    lf = LorentzianFit(xdata=d.index, ydata=d.values)
    lf.minimize()
    print(lf.func_label)
    print(lf.pretty_params)

    pvf = PsVoigtFit(xdata=d.index, ydata=d.values)
    pvf.minimize()
    print(pvf.func_label)
    print(pvf.pretty_params)

    plt.figure()
    plt.plot(gf.xdata, gf.ydata, linestyle='', marker='o')
    plt.plot(gf.xdata, gf.fit_ydata, label='Gaussian')
    plt.plot(lf.xdata, lf.fit_ydata, label='Lorentzian')
    plt.plot(pvf.xdata, pvf.fit_ydata, label='p.-Voigt')
    plt.legend()
    plt.show()
