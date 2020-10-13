import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
import torch


def plot_prep(x):
    return {'x': x.index, 'y': x['counts'],
            'yerr': np.sqrt(x['counts']),
            'marker': '.', 'linestyle': ''}


def t_entropy(pp):
    return -torch.sum(pp * torch.log(pp))


def t_c0(pp, ww=None):
    if ww is not None:
        return torch.abs(torch.sum(ww * pp))
    else:
        return torch.abs(torch.sum(pp))


def t_c1(pp, oo, ww):
    return torch.mean(ww * (pp - oo) ** 2)


def t_c2(pp, ww):
    return torch.mean(ww[:-1] * (pp[:-1] - pp[1:]) ** 2)


def maximize_entropy(observed: np.ndarray, weights: np.ndarray):
    """"""
    observed = torch.tensor(observed, requires_grad=False)
    weights = torch.tensor(weights, requires_grad=False)

    predicted = observed.detach().clone()
    track = {'S': [], 'c0': [], 'c1': [], 'c2': []}

    lr = 1E-2
    chisqr_window = 1E-2
    for ii in range(30000):

        p_s, p_c0, p_c1, p_c2 = (predicted.detach().clone().requires_grad_(True),
                                 predicted.detach().clone().requires_grad_(True),
                                 predicted.detach().clone().requires_grad_(True),
                                 predicted.detach().clone().requires_grad_(True))

        ent = -t_entropy(p_s)
        ent.backward()
        grad = p_s.grad

        c2 = t_c2(p_c2, weights)
        if c2.data > 0.3:
            c2.backward()
            c2_grad = p_c2.grad
            if torch.norm(c2_grad) > 0:
                c2_grad = c2_grad / torch.norm(c2_grad)
                grad = c2_grad * torch.dot(grad, c2_grad)

        c0 = t_c0(p_c0)
        c0.backward()
        c0_grad = p_c0.grad
        if torch.norm(c0_grad) > 0:
            c0_grad = c0_grad / torch.norm(c0_grad)
            grad = grad - c0_grad * torch.dot(grad, c0_grad)

        c1 = t_c1(p_c1, observed, weights)
        if 1. - chisqr_window <= c1.data <= 1. + chisqr_window:
            c1.backward()
            c1_grad = p_c1.grad
            if torch.norm(c1_grad) > 0:
                c1_grad = c1_grad / torch.norm(c1_grad)
                grad = grad - c1_grad * torch.dot(grad, c1_grad)

        track['S'].append(-ent.data)
        track['c0'].append(c0.data)
        track['c1'].append(c1.data)
        track['c2'].append(c2.data)

        predicted -= lr * grad
        print("%d :: S=%f : c0=%f : c1=%f : c2=%f" % (ii, track['S'][-1], track['c0'][-1],
                                                      track['c1'][-1], track['c2'][-1]))

    plt.figure()
    ax = plt.subplot(411)
    plt.title('Entropy maximization track')
    plt.plot(track['S'], label='Entropy')
    plt.legend()
    plt.subplot(412, sharex=ax)
    plt.plot(track['c0'], label='Total count')
    plt.legend()
    plt.subplot(413, sharex=ax)
    plt.plot(track['c1'], label='$\chi^{2}$')
    plt.legend()
    plt.subplot(414, sharex=ax)
    plt.plot(track['c2'], label='E[dy/dx]')
    plt.legend()
    plt.show()

    return predicted.detach().data


if __name__ == '__main__':
    wd = os.path.join('..', '..', 'test_files', 'generated', 'probe_5-5_sin2psi')

    for f_name in os.listdir(wd):
        dd = pd.read_csv(os.path.join(wd, f_name), header=0, index_col='eV', dtype=np.float)

        # dd = dd[62000:65000]
        xx, yy = np.array(dd.index).flatten(), np.array(dd.values).flatten()
        xx, yy = xx[(~np.isnan(yy)) & (yy > 0)], yy[(~np.isnan(yy)) & (yy > 0)]

        yy_opt = maximize_entropy(yy, np.ones(shape=yy.shape) * yy.shape[0] / np.sum(yy))

        plt.plot(xx, yy, linestyle='', marker='.')
        plt.plot(xx, yy_opt, linestyle='--', marker='')
        plt.show()
