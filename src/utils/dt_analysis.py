import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import


if __name__ == '__main__':
    wds = ('Mo1', 'Pb1', 'Ta1', 'Wolfram3')

    fig = plt.figure()
    ax = (fig.add_subplot(121, projection='3d'), fig.add_subplot(122, projection='3d'))
    ax[0].set_zlim3d(-0.4, 0.4)
    ax[1].set_zlim3d(-0.025, 0.025)

    ax[0].set_title('Channel 0')
    ax[1].set_title('Channel 1')

    ax[0].set_xlabel('Log10[Dead time]')
    ax[0].set_ylabel('Energy [keV]')
    ax[0].set_zlabel('Energy shift [keV]')

    ax[1].set_xlabel('Log10[Dead time]')
    ax[1].set_ylabel('Energy [keV]')
    ax[1].set_zlabel('Energy shift [keV]')

    for wd in wds:
        for ch in 0, 1:
            d1 = pd.read_csv(os.path.join(r'C:\Users\dovzheng\Experiments\2020-12-04_DT_Tests', wd,
                                          'peaks_ch%d.csv' % ch))
            for ii in range(5):
                if 'pv%d_center' % ii in d1.columns:
                    dt = np.array(d1['DeadTime'])
                    en = np.array(d1['pv%d_center' % ii])
                    d_en = en - np.mean(en)
                    en, dt = en[np.abs(d_en) < 0.1], dt[np.abs(d_en) < 0.1]
                    d_en = en - np.mean(en)
                    ax[ch].scatter(np.log10(dt), en, d_en)
    plt.show()