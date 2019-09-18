import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
from scipy.optimize import curve_fit


def fit_peak(dd):
    fit_peak.fn = lambda x, *args: args[0] * np.exp(-0.5 * args[1] * (x - args[2]) ** 2) + args[3] * x + args[4]
    popt, pcov = curve_fit(f=fit_peak.fn, xdata=dd.index, ydata=dd.values,
                           p0=[dd.max(), 0.1, dd.idxmax(), 0., dd.min()])
    perr = np.sqrt(np.diag(pcov))
    return popt, perr


if __name__ == '__main__':
    register_matplotlib_converters()

    data = pd.read_csv('test_files/exposures2.csv', index_col=0)
    data.columns = data.columns.astype('int')
    data.set_index(pd.to_datetime(data.index, format="Co57_%Y-%m-%d::%H:%M:%S_.nxs"), inplace=True)
    data.sort_index(inplace=True)

    img_data = data.iloc[:, 3940:4020].apply(fit_peak, axis=1)
    img_data = pd.DataFrame({'amp': img_data.apply(lambda x: x[0][0]),
                             'amp_err': img_data.apply(lambda x: x[1][0]),
                             'sig': img_data.apply(lambda x: x[0][1]),
                             'sig_err': img_data.apply(lambda x: x[1][1]),
                             'pos': img_data.apply(lambda x: x[0][2]),
                             'pos_err': img_data.apply(lambda x: x[1][2])})

    total_data = data.sum(axis=0)
    po, pc = fit_peak(total_data[3940:4020])

    plt.plot(total_data)
    plt.plot(np.arange(3940, 4020), fit_peak.fn(np.arange(3940, 4020), *po))
    plt.show()
    total_data = pd.DataFrame({'amp': [po[0]] * img_data.shape[0],
                               'amp_err': [pc[0]] * img_data.shape[0],
                               'sig': [po[1]] * img_data.shape[0],
                               'sig_err': [pc[1]] * img_data.shape[0],
                               'pos': [po[2]] * img_data.shape[0],
                               'pos_err': [pc[2]] * img_data.shape[0]},
                              index=img_data.index)

    img_data['r_amp'] = (img_data['amp'] - po[0] / img_data.shape[0]) / (po[0] / img_data.shape[0])
    img_data['r_amp_err'] = img_data['amp_err'] / (po[0] / img_data.shape[0])
    img_data['r_sig'] = (img_data['sig'] - po[1]) / po[1]
    img_data['r_sig_err'] = img_data['sig_err'] / po[1]
    img_data['r_pos'] = (img_data['pos'] - po[2]) / po[2]
    img_data['r_pos_err'] = img_data['pos_err'] / po[2]

    plt.figure('Real values')
    plt.subplot(311)
    plt.errorbar(x=img_data.index, y=img_data['amp'], yerr=img_data['amp_err'])
    plt.errorbar(x=total_data.index, y=total_data['amp'] / total_data.shape[0],
                 yerr=total_data['amp_err'] / total_data.shape[0])
    plt.ylabel('Amplitude')
    plt.subplot(312)
    plt.errorbar(x=img_data.index, y=img_data['sig'], yerr=img_data['sig_err'])
    plt.errorbar(x=total_data.index, y=total_data['sig'], yerr=total_data['sig_err'])
    plt.ylabel('$\sigma$')
    plt.subplot(313)
    plt.errorbar(x=img_data.index, y=img_data['pos'], yerr=img_data['pos_err'])
    plt.errorbar(x=total_data.index, y=total_data['pos'], yerr=total_data['pos_err'])
    plt.ylabel('Position')
    plt.tight_layout()

    plt.figure('Relative values')
    plt.subplot(311)
    plt.errorbar(x=img_data.index, y=img_data['amp'] / po[0], yerr=img_data['amp_err'] / po[0])
    plt.errorbar(x=total_data.index, y=total_data['amp'] / (total_data.shape[0] * po[0]),
                 yerr=total_data['amp_err'] / (total_data.shape[0] * po[0]))
    plt.ylabel('Amplitude')
    plt.subplot(312)
    plt.errorbar(x=img_data.index, y=img_data['sig'] / po[1], yerr=img_data['sig_err'] / po[1])
    plt.errorbar(x=total_data.index, y=total_data['sig'] / po[1], yerr=total_data['sig_err'] / po[1])
    plt.ylabel('$\sigma$')
    plt.subplot(313)
    plt.errorbar(x=img_data.index, y=img_data['pos'] / po[2], yerr=img_data['pos_err'] / po[2])
    plt.errorbar(x=total_data.index, y=total_data['pos'] / po[2], yerr=total_data['pos_err'] / po[2])
    plt.ylabel('Position')
    plt.tight_layout()

    plt.figure('Correlations')
    plt.subplot(221)
    plt.plot(img_data['r_amp'], img_data['r_pos'], marker='o', linestyle='')
    plt.xlabel('Amplitude')
    plt.ylabel('Peak position')
    plt.subplot(222)
    plt.plot(img_data['r_amp'], img_data['r_sig'], marker='o', linestyle='')
    plt.xlabel('Amplitude')
    plt.ylabel('Peak width')
    plt.subplot(223)
    plt.plot(img_data['r_pos'], img_data['r_sig'], marker='o', linestyle='')
    plt.xlabel('Peak position')
    plt.ylabel('Peak width')
    plt.tight_layout()
    plt.show()
