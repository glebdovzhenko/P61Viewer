import h5py
import json
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import os


if __name__ == '__main__':
    wd = 'test_files/pwdr_csv'
    dd = 'test_files/pwdr_h5'
    for ii, f_name in enumerate(sorted(os.listdir(wd))):
        print(os.path.join(wd, f_name))
        d = pd.read_csv(os.path.join(wd, f_name), skiprows=12, header=0)
        d.drop(['y_calc', 'y_bkg', 'Q'], axis=1, inplace=True)
        d.rename(columns={'x': 'Tth', 'y_obs': 'Int'}, inplace=True)

        # photon energy for energy-dispersive diffraction at 6 degrees
        d['keV'] = 833486.581598987 * np.sin(d['Tth'] * np.pi / 180.) * 1E-3
        d = d[(d['keV'] > 40) & (d['keV'] < 100)]

        with h5py.File(os.path.join(dd, 'Al2236_%05d.h5' % ii), 'w') as f:
            dset = f.create_dataset("Spectrum", data=np.array(d[['keV', 'Int']]))
            md = f.create_dataset("Metadata", data=json.dumps({'MOTPOS1': 0.0, 'MOTPOS2': float(ii) - 4.2 - 0.5 * np.random.rand()}))

        plt.plot(d['keV'], d['Int'], label=f_name)
        plt.legend()
        plt.show()
