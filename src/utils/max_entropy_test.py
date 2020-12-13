import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
import torch
from src.DatasetIO import P61ANexusReader, EDDIReader


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


def project(t1, t2):
    return t2 * torch.dot(t1, t2) / torch.sum(t2 ** 2)


def reject(t1, t2):
    return t1 - project(t1, t2)


def maximize_entropy(observed: np.ndarray, weights: np.ndarray):
    """"""
    observed = torch.tensor(observed, requires_grad=False)
    weights = torch.tensor(weights, requires_grad=False)

    predicted = observed.detach().clone()
    track = {'S': [], 'c0': [], 'c1': [], 'c2': []}

    lr = 1E-2
    chisqr_window = 1E-2
    for ii in range(5000):

        p_s, p_c0, p_c1, p_c2 = (predicted.detach().clone().requires_grad_(True),
                                 predicted.detach().clone().requires_grad_(True),
                                 predicted.detach().clone().requires_grad_(True),
                                 predicted.detach().clone().requires_grad_(True))

        ent = -t_entropy(p_s)
        ent.backward()
        grad = p_s.grad

        c2 = t_c2(p_c2, weights)
        c2.backward()
        if torch.norm(p_c2.grad) > 0:
            grad = project(grad, p_c2.grad)

        c0 = t_c0(p_c0)
        c0.backward()
        if torch.norm(p_c0.grad) > 0:
            grad = reject(grad, p_c0.grad)

        c1 = t_c1(p_c1, observed, weights)
        c1.backward()
        if 1. - chisqr_window <= c1.data <= 1. + chisqr_window:
            if torch.norm(p_c1.grad) > 0:
                grad = reject(grad, p_c1.grad)

        track['S'].append(-ent.data)
        track['c0'].append(c0.data)
        track['c1'].append(c1.data)
        track['c2'].append(c2.data)

        predicted -= lr * grad
        if ii % 100 == 0:
            print("%d :: S=%f : Sum=%f : chisqr=%f : E[dy/dx]=%f" %
                  (ii, track['S'][-1], track['c0'][-1], track['c1'][-1], track['c2'][-1]))

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
    # reader = EDDIReader()
    # data = reader.read(r'C:\Users\dovzheng\PycharmProjects\P61Viewer\test_files\collected\Probe_5-5_sin2psi_04082015')

    reader = P61ANexusReader()
    wd = r'C:\Users\dovzheng\Experiments\2020-12-11_Diffraction5'
    data = pd.DataFrame(columns=reader.columns)
    for f_name in os.listdir(wd)[150:170]:
        data = pd.concat((data, reader.read(os.path.join(wd, f_name))), ignore_index=True)

    for ii in data.index:
        xx, yy = data.loc[ii, 'DataX'].astype(np.float), data.loc[ii, 'DataY'].astype(np.float)
        print(data.loc[ii, 'ScreenName'])
        xx_, yy = xx[(~np.isnan(yy)) & (yy > 0)], yy[(~np.isnan(yy)) & (yy > 0)]
        if yy.shape[0] == 0:
            continue

        yy_opt = maximize_entropy(yy, np.ones(shape=yy.shape) * yy.shape[0] / np.sum(yy))
        yy_opt = np.interp(xx, xx_, yy_opt)
        plt.plot(xx_ * 1E-3, yy, linestyle='', marker='.', label='Observed')
        plt.plot(xx * 1E-3, yy_opt, linestyle='--', marker='', label='MEM optimized')
        plt.xlabel('Energy, keV')
        plt.ylabel('Intensity, counts')
        plt.legend()
        plt.show()
