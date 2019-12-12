from PyQt5.QtWidgets import QWidget, QErrorMessage
import h5py
import numpy as np
import pandas as pd
import os
import struct

from P61App import P61App


class FileImportWidget(QWidget):
    """
    Module responsible for importing files
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

    @staticmethod
    def print_attrs(name, obj):
        if isinstance(obj, h5py.Dataset):
            print(name, np.array(obj))

    def open_nxs_file(self, f_name):
        ch0, ch1 = 'entry/instrument/xspress3/channel00/histogram', \
                   'entry/instrument/xspress3/channel01/histogram'
        columns = list(self.q_app.data.columns)
        failed = []
        kev_per_bin = 5E-2

        for ii, channel in enumerate((ch0, ch1)):
            try:
                with h5py.File(f_name, 'r') as f:
                    frames = np.sum(f[channel], axis=0)
                    frames[:20] = 0.0
                    frames[-1] = 0.0
                    kev = (np.arange(frames.shape[0]) + 0.5) * kev_per_bin

                    row = {c: None for c in columns}
                    row.update({
                        'DataX': kev,
                        'DataY': frames,
                        'DataID': f_name + ':' + channel,
                        'ScreenName': os.path.basename(f_name) + ':' + '%02d' % ii,
                        'Active': True,
                        'Color': next(self.q_app.params['ColorWheel'])
                    })

                    self.q_app.data.loc[len(self.q_app.data.index)] = row

            except Exception as e:
                print(e)
                failed.append(f_name + '::' + channel)

        return failed

    def open_raw_file(self, f_name):
        int_size = 4  # bytes

        columns = list(self.q_app.data.columns)
        edep = []

        bins = 2**14
        kev_per_bin = 1E-3

        try:
            with open(f_name, 'rb') as f:
                _, _, _, nos = struct.unpack('hhhh', f.read(2 * int_size))
                event_size = 8 * int_size * nos

            with open(f_name, 'rb') as f:
                event = f.read(event_size)

                while event != b'':
                    edep.append(struct.unpack('H' * 2 * 8 * nos, event)[4])
                    event = f.read(event_size)

                values, bins = np.histogram(edep, bins=bins)

                row = {c: None for c in columns}
                row.update({
                    'DataX': kev_per_bin * bins[:-1],
                    'DataY': values,
                    'DataID': f_name,
                    'ScreenName': os.path.basename(f_name),
                    'Active': True,
                    'Color': next(self.q_app.params['ColorWheel'])
                })

                self.q_app.data.loc[len(self.q_app.data.index)] = row
                return []
        except Exception as e:
            print(e)
            return [f_name]

    def open_csv_file(self, f_name):
        columns = list(self.q_app.data.columns)

        try:
            dd = pd.read_csv(f_name, skiprows=6, skipfooter=1, header=None, names=['keV', '00', '01'])
        except Exception as e:
            print(e)
            return [f_name + ':channel0', f_name + ':channel1']

        for ch in ('00', '01'):
            row = {c: None for c in columns}
            row.update({
                'DataX': 1E-3 * dd['keV'],
                'DataY': dd[ch],
                'DataID': f_name + ':' + ch,
                'ScreenName': os.path.basename(f_name) + ':' + ch,
                'Active': True,
                'Color': next(self.q_app.params['ColorWheel'])
            })

            self.q_app.data.loc[len(self.q_app.data.index)] = row
        return []

    def open_files(self, f_names):
        # TODO: add check if the files are already open
        failed = []
        opened = 0
        for ff in f_names:
            if '.nxs' in ff:
                fld = self.open_nxs_file(ff)
                opened += 2 - len(fld)
                failed.extend(fld)
            elif '.raw' in ff:
                fld = self.open_raw_file(ff)
                opened += 1 - len(fld)
                failed.extend(fld)
            elif '.csv' in ff:
                fld = self.open_csv_file(ff)
                opened += 2 - len(fld)
                failed.extend(fld)

        self.q_app.dataRowsAppended.emit(opened)

        if failed:
            msg = QErrorMessage()
            msg.showMessage('Could not open files:\n' + '\n'.join(failed))
            msg.exec_()


if __name__ == '__main__':
    import sys
    q_app = P61App(sys.argv)
    wg = FileImportWidget()
    wg.open_files(
        ['/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/collected/Co57_2019-09-30_09-10-30_.nxs',
         '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/collected/Co57_2019-09-30_09-27-11_.nxs',
         '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/collected/Co57_2019-09-30_09-43-51_.nxs',
         '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/collected/Co57_2019-09-30_10-00-32_.nxs',
         '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/collected/Co57_2019-09-30_10-17-13_.nxs'])
    print(q_app.data)
    print(q_app.data.loc[0])
    sys.exit(q_app.exec())
