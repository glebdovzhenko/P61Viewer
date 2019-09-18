import h5py
import json
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import os


if __name__ == '__main__':
    wd = 'test_files/pwdr_csv'
    dd = 'test_files/pwdr_nexus'

    tmpl = 'Al2236-%05d_tif_A%d.csv'
    n_bins = 4096

    for ii in range(65, 91):
        f1, f2 = tmpl % (ii, 0), tmpl % (ii, 90)
        result = dict()
        for jj, f_name in enumerate((f1, f2)):
            d = pd.read_csv(os.path.join(wd, f_name), skiprows=12, header=0)
            d.drop(['y_calc', 'y_bkg', 'Q'], axis=1, inplace=True)
            d.rename(columns={'x': 'Tth', 'y_obs': 'Int'}, inplace=True)

            # photon energy for energy-dispersive diffraction at 6 degrees
            d['keV'] = 833486.581598987 * np.sin(d['Tth'] * np.pi / 180.) * 1E-3

            new_bins = np.linspace(0, 100, 4096)
            new_d = d.set_index('keV')['Int'].copy()
            new_d = new_d.reindex(new_d.index.union(new_bins), method=None)
            new_d.interpolate(method='linear', inplace=True)
            new_d.drop(d['keV'], inplace=True)
            new_d.fillna(method='bfill', inplace=True)
            result['entry/instrument/xspress3/channel%02d/histogram' % jj] = np.array(new_d.values).reshape((1, new_d.shape[0]))
        print(result)

        with h5py.File(os.path.join(dd, 'Al2236_%05d.nxs' % ii), 'w') as f:
            for k in result.keys():
                print(result[k])
                dset = f.create_dataset(k, data=result[k])

        plt.plot(d['keV'], d['Int'], label='original')
        plt.plot(new_d, label='New')
        plt.axis((0, 100, 0, 10000))
        plt.legend()
        plt.show()
