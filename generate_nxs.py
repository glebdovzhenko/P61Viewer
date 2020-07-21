import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import h5py


dd = '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/generated'


def p_voigt(xx_, a, x0, n, s, g):
    return a * (n * np.exp((xx_ - x0) ** 2 / (-2. * s ** 2)) + (1. - n) * (g ** 2) /
                ((xx_ - x0) ** 2 + g ** 2))


if __name__ == '__main__':
    n_bins = 4096

    xx = np.arange(n_bins) * 5E-2
    yy = 10 * np.random.random(n_bins)
    for ii, ww in enumerate(np.logspace(-2, 0.1, 10)):
        yy += p_voigt(xx, a=1E3, x0=10 + 15 * ii, n=1.3E-1, s=ww, g=ww)

    plt.plot(xx, yy)
    plt.show()

    with h5py.File(os.path.join(dd, 'test_width.nxs'), 'w') as f:
        f.create_dataset('entry/instrument/xspress3/channel00/histogram', data=yy.reshape((1, n_bins)))
