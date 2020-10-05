import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os


def plot_prep(x):
    return {'x': x.index, 'y': x['counts'],
            'yerr': np.sqrt(x['counts']),
            'marker': '.', 'linestyle': ''}


def max_entropy_method(observed, weights):
    """
    :param observed:
    :return:

    Entropy:
        S = -1. * np.sum(mem_predicted * np.log(mem_predicted))

    Constraints:
        0: np.sum(mem_predicted) - np.sum(observed) = 0
        1: np.mean(weights * (observed - mem_predicted) ** 2) - 1 = 0

    Calculation:
        mem_predicted = np.exp(
            - lambdas[0]
            - lambdas[1] * 2. * weights * (observed - mem_predicted)  / observed.shape[0]
            )
    """


if __name__ == '__main__':
    wd = os.path.join('..', '..', 'test_files', 'generated', 'probe_5-5_sin2psi')

    for f_name in os.listdir(wd):
        dd = pd.read_csv(os.path.join(wd, f_name), header=0, index_col='eV')

        dd = dd[62000:65000]
        plt.errorbar(**plot_prep(dd))
        plt.show()

        max_entropy_method(dd.values, np.array([dd.shape[0] / dd.sum()] * dd.shape[0]))
        break