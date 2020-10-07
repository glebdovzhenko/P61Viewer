import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
import torch


def plot_prep(x):
    return {'x': x.index, 'y': x['counts'],
            'yerr': np.sqrt(x['counts']),
            'marker': '.', 'linestyle': ''}


def max_entropy_method(observed, weights, delta):
    """
    :param observed:
    :return:

    """

    mem_predicted = torch.tensor(observed, requires_grad=True)
    observed = torch.tensor(observed)
    weights = torch.tensor(weights)
    lambdas = torch.tensor([1., 1., 1.], requires_grad=True)

    optimizer = torch.optim.Adam([mem_predicted, lambdas], lr=1E-3)
    for i in range(30000):
        optimizer.zero_grad()

        tmp = 0.5 * (torch.cat((mem_predicted[1:], torch.tensor([0.], dtype=torch.double))) + torch.cat((torch.tensor([0.], dtype=torch.double), mem_predicted[:-1])))

        metric = torch.sum(torch.abs(
            torch.log(mem_predicted) + 1. +
            lambdas[0] * mem_predicted +
            lambdas[1] * 2. * weights * (mem_predicted - observed) / observed.shape[0] +
            lambdas[2] * 2. * weights * (mem_predicted - tmp) / observed.shape[0]
        ))
        metric += torch.abs(
            torch.sum(mem_predicted) - torch.sum(observed)
        )
        metric += torch.abs(
            torch.mean(weights * (mem_predicted - observed) ** 2) - 1.
        )
        metric += torch.abs(
            torch.mean(weights * (mem_predicted - tmp) ** 2) - delta
        )

        metric.backward()
        optimizer.step()

        if (i + 1) % 1000 == 0:
            with torch.no_grad():
                print(i + 1, lambdas, metric, torch.sum(mem_predicted), torch.sum(observed))

    return mem_predicted.detach().numpy()


if __name__ == '__main__':
    wd = os.path.join('..', '..', 'test_files', 'generated', 'probe_5-5_sin2psi')

    for f_name in os.listdir(wd):
        dd = pd.read_csv(os.path.join(wd, f_name), header=0, index_col='eV', dtype=np.float)

        dd = dd[62000:65000]
        xx, yy = np.array(dd.index).flatten(), np.array(dd.values).flatten()
        xx, yy = xx[(~np.isnan(yy)) & (yy > 0)], yy[(~np.isnan(yy)) & (yy > 0)]

        predicted = max_entropy_method(yy, np.sqrt(yy), 0.1)

        plt.plot(xx, yy, '.-')
        plt.plot(xx, predicted)
        plt.show()
