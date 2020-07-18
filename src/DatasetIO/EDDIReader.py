import h5py
import numpy as np
import pandas as pd
import os

from P61App import P61App


class EDDIReader:
    comments = ('#F', '#E', '#D', '#C')

    def __init__(self):
        self.q_app = P61App.instance()

    def validate(self, f_name):
        try:
            with open(f_name, 'r') as f:
                for ii in range(4):
                    line = f.readline()
                    if line[:2] != self.comments[ii]:
                        return False
                return True
        except Exception:
            return False

    def read(self, f_name):
        result = pd.DataFrame(columns=self.q_app.data.columns)
        kev_per_bin = 1.25E-2

        with open(f_name, 'r') as f:
            buffer = None
            index = 0
            for line in f.readlines():
                if len(line) < 3:
                    buffer = None
                elif line[0] == '#':
                    buffer = None
                    if line[:2] == '#S':
                        index = int(line.split(' ')[1])
                elif line[:2] == '@A':
                    buffer = []
                    buffer.extend(filter(lambda x: bool(x),
                                         line.replace('@A', '').replace('\\', '').replace('\n', '').split(' ')))
                elif line[-2] == '\\':
                    buffer.extend(filter(lambda x: bool(x),
                                         line.replace('@A', '').replace('\\', '').replace('\n', '').split(' ')))
                elif buffer is not None:
                    buffer.extend(filter(lambda x: bool(x),
                                         line.replace('@A', '').replace('\\', '').replace('\n', '').split(' ')))

                    buffer = np.array(list(map(int, buffer)), dtype=np.float)
                    kev = np.arange(buffer.shape[0]) * kev_per_bin

                    row = {c: None for c in self.q_app.data.columns}

                    row.update({
                        'DataX': kev,
                        'DataY': buffer,
                        'DataID': f_name + ':S%03d' % index,
                        'ScreenName': os.path.basename(f_name) + ':S%03d' % index,
                        'Active': True,
                        'Color': next(self.q_app.params['ColorWheel'])
                    })

                    result.loc[result.shape[0]] = row
                    buffer = None

            result = result.astype('object')
            result[pd.isna(result)] = None
            return result
