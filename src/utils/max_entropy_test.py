import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
import torch


def plot_prep(x):
    return {'x': x.index, 'y': x['counts'],
            'yerr': np.sqrt(x['counts']),
            'marker': '.', 'linestyle': ''}


def max_entropy_torch(observed, weights, delta):
    """
    :param observed:
    :return:

    """

    def upd_prediction():
        average = 0.5 * (torch.cat((mem_predicted[1:], torch.tensor([mem_predicted.data[-1]], dtype=torch.double))) +
                         torch.cat((torch.tensor([mem_predicted.data[0]], dtype=torch.double), mem_predicted[:-1])))

        return torch.exp(
            - l0
            - l1 * 2. * weights * (mem_predicted - observed) / mem_predicted.shape[0]
            - l2 * 4. * weights * (mem_predicted - average) / mem_predicted.shape[0]
        )

    def c0():
        return torch.abs(torch.sum(mem_predicted - observed))

    def c1():
        return torch.abs(torch.mean(weights * (mem_predicted - observed) ** 2) - 1.)

    def c2():
        return torch.mean(weights[:-1] * (mem_predicted[:-1] - mem_predicted[1:]) ** 2)

    def status():
        return 'c0: %f, c1: %f, c2: %f -- l0: %f, l1: %f, l2: %f' %\
               (c0().data, c1().data, c2().data, l0.data, l1.data, l2.data)

    track = {'c0': [], 'c1': [], 'c2': []}

    mem_predicted = torch.tensor(observed, requires_grad=True)
    observed = torch.tensor(observed)
    weights = torch.tensor(weights)
    l0, l1, l2 = torch.tensor(-1.59, requires_grad=True), \
                 torch.tensor(2.68, requires_grad=True), \
                 torch.tensor(0., requires_grad=True)

    outer_opt = torch.optim.Adam([l1], lr=1E-3)
    inner_opt = torch.optim.Adam([mem_predicted, l0], lr=1E-3)

    mem_predicted = upd_prediction()
    # l1 = l1.detach()
    i = 0
    while c1().data > 40:
        for _ in range(100):
            outer_opt.zero_grad()
            mem_predicted = upd_prediction()

            metric = c1()
            metric.backward(retain_graph=True)
            outer_opt.step()

            j = 0

        while c0().data > 10:
            inner_opt.zero_grad()
            mem_predicted = upd_prediction()

            metric = c0()
            metric.backward(retain_graph=True)
            inner_opt.step()
            track['c0'].append(c0().data)
            track['c1'].append(c1().data)
            track['c2'].append(c2().data)

            if j % 10 == 0:
                print(i, j, 'c0: %f, c1: %f, c2: %f -- l0: %f, l1: %f, l2: %f' %
                      (c0().data, c1().data, c2().data, l0.data, l1.data, l2.data))
            j += 1

        if i % 10 == 0:
            print(i, j, 'c0: %f, c1: %f, c2: %f -- l0: %f, l1: %f, l2: %f' %
                  (c0().data, c1().data, c2().data, l0.data, l1.data, l2.data))
        i += 1

    for lbl in ('c0', 'c1', 'c2'):
        plt.plot(track[lbl], label=lbl)
        plt.legend()
    plt.show()

    return mem_predicted.detach().numpy()


def max_entropy_numpy(observed, weights, delta):
    def upd_prediction():
        average = 0.5 * (np.concatenate((mem_predicted[1:], np.array([mem_predicted[-1]]))) +
                         np.concatenate((np.array([mem_predicted[0]]), mem_predicted[:-1])))
        return np.exp(
            - l0
            - l1 * 2. * weights * (mem_predicted - observed) / mem_predicted.shape[0]
            - l2 * 4. * weights * (mem_predicted - average) / mem_predicted.shape[0]
        )

    def chisqr():
        return np.mean(weights * (mem_predicted - observed) ** 2)

    def c0():
        return np.abs(np.sum(mem_predicted - observed))

    def c1():
        return np.abs(np.mean(weights * (mem_predicted - observed) ** 2) - 1.)

    def c2():
        return np.mean(weights[:-1] * (mem_predicted[:-1] - mem_predicted[1:]) ** 2)

    l0, l1, l2 = 1E-3, 1E-3, 1E-3
    mem_predicted = upd_prediction(observed.copy())

    for _ in range(10):
        l1 *= np.mean(weights * (mem_predicted - observed) ** 2)
        mem_predicted = upd_prediction(mem_predicted)
        print('c0: %f, c1: %f, c2: %f -- l0: %f, l1: %f, l2: %f' %
              (c0(mem_predicted), c1(mem_predicted), c2(mem_predicted), l0, l1, l2))

    return mem_predicted


if __name__ == '__main__':
    wd = os.path.join('..', '..', 'test_files', 'generated', 'probe_5-5_sin2psi')

    for f_name in os.listdir(wd):
        dd = pd.read_csv(os.path.join(wd, f_name), header=0, index_col='eV', dtype=np.float)

        dd = dd[62000:65000]
        xx, yy = np.array(dd.index).flatten(), np.array(dd.values).flatten()
        xx, yy = xx[(~np.isnan(yy)) & (yy > 0)], yy[(~np.isnan(yy)) & (yy > 0)]

        predicted = max_entropy_torch(yy, np.sqrt(yy), 0.1)
        # predicted = max_entropy_numpy(yy, np.sqrt(yy), 0.1)

        plt.plot(xx, yy, '.-')
        plt.plot(xx, predicted)
        plt.show()
        break
