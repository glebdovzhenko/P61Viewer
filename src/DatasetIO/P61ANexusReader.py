import h5py
import numpy as np
import pandas as pd
import os

from P61App import P61App


class P61ANexusReader:
    ch0 = ('entry', 'instrument', 'xspress3', 'channel00')
    ch1 = ('entry', 'instrument', 'xspress3', 'channel01')
    all_event = ('scaler', 'allevent')
    all_good = ('scaler', 'allgood')
    hist = ('histogram', )
    columns = ('DataX', 'DataY', 'DataID', 'Channel', 'ScreenName', 'Active', 'Color', 'DeadTime')

    def __init__(self):
        self.q_app = P61App.instance()

    def validate(self, f_name):
        hists = False
        try:
            with h5py.File(f_name, 'r') as f:
                hists |= '/'.join(self.ch0 + self.hist) in f
                hists |= '/'.join(self.ch1 + self.hist) in f
        except Exception:
            return False

        return hists

    def read(self, f_name, sum_frames=True):
        kev_per_bin = 5E-2
        if self.q_app is not None:
            result = pd.DataFrame(columns=self.q_app.data.columns)
        else:
            result = pd.DataFrame(columns=self.columns)

        with h5py.File(f_name, 'r') as f:
            for ii, channel in enumerate((self.ch0, self.ch1)):
                if '/'.join(channel + self.hist) not in f:
                    continue

                frames = np.sum(f['/'.join(channel + self.hist)], axis=0)
                frames[:20] = 0.0
                frames[-1] = 0.0
                kev = (np.arange(frames.shape[0]) + 0.5) * kev_per_bin

                if self.q_app is not None:
                    row = {c: None for c in self.q_app.data.columns}
                else:
                    row = {c: None for c in self.columns}

                if ('/'.join(channel + self.all_event) in f) and ('/'.join(channel + self.all_good) in f):
                    allevent = np.sum(f['/'.join(channel + self.all_event)], axis=0)
                    allgood = np.sum(f['/'.join(channel + self.all_good)], axis=0)
                    row.update({'DeadTime': 1. - allgood / allevent})

                row.update({
                    'DataX': kev,
                    'DataY': frames,
                    'DataID': f_name + ':' + '/'.join(channel),
                    'Channel': ii,
                    'ScreenName': os.path.basename(f_name) + ':' + '%02d' % ii,
                    'Active': True,
                })

                if self.q_app is not None:
                    row.update({'Color': next(self.q_app.params['ColorWheel'])})
                result.loc[result.shape[0]] = row

        result = result.astype('object')
        result[pd.isna(result)] = None
        return result
