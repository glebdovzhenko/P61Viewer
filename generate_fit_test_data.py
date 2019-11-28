import os
import numpy as np
from matplotlib import pyplot as plt
import h5py


dd = '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/fit_test'


def p_voigt(a, x0, n, s, g):
    return a * (n * np.exp((np.arange(n_bins) - x0) ** 2 / (-2. * s ** 2)) + (1. - n) * (g ** 2) /
                ((np.arange(n_bins) - x0) ** 2 + g ** 2))


if __name__ == '__main__':
    n_bins = 4096

    for ii in range(50):
        data_y = np.zeros(n_bins)
        data_y += 10 * np.random.random(n_bins)
        data_y += p_voigt(a=100, x0=2000 + ii, n=0.95, s=10, g=10)
        data_y = data_y.reshape((1, n_bins))

        with h5py.File(os.path.join(dd, 'single_peak%05d.nxs' % (ii / 2)), 'a') as f:
            if 'entry/instrument/xspress3/channel%02d/histogram' % (ii % 2) not in f.keys():
                dset = f.create_dataset('entry/instrument/xspress3/channel%02d/histogram' % (ii % 2), data=data_y)
            else:
                tmp = f['entry/instrument/xspress3/channel%02d/histogram' % (ii % 2)]
                tmp[...] = data_y
