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

        return 2 - len(failed), failed

    def open_raw_file(self, f_name):
        """
        """
        int_size = 4  # bytes
        columns = list(self.q_app.data.columns)
        kev_per_bin = 1E-3
        failed = []

        try:
            with open(f_name, 'rb') as f:
                _, _, _, nos = struct.unpack('hhhh', f.read(2 * int_size))
                event_size = 8 * int_size * nos

            with open(f_name, 'rb') as f:
                event = f.read(event_size)
                channels = dict()
                while event != b'':
                    edep = int.from_bytes(event[8:10], byteorder='little')
                    channel = event[1]
                    if channel not in channels:
                        channels[channel] = [edep]
                    else:
                        channels[channel].append(edep)
                    event = f.read(event_size)
        except Exception as e:
            print(e)
            return 0, [f_name + ':00', f_name + ':01']

        for ch in channels:
            try:
                values, bins = np.histogram(channels[ch], bins=2**16)
                bins = bins[:-1] + 0.5
                bins = bins[values != 0]
                values = values[values != 0]

                row = {c: None for c in columns}
                row.update({
                    'DataX': kev_per_bin * bins,
                    'DataY': values,
                    'DataID': f_name + ':%02d' % ch,
                    'ScreenName': os.path.basename(f_name) + ':%02d' % ch,
                    'Active': True,
                    'Color': next(self.q_app.params['ColorWheel'])
                })

                self.q_app.data.loc[len(self.q_app.data.index)] = row
            except Exception as e:
                print(e)
                failed.append(f_name + ':%02d' % ch)

        return 2 - len(failed), failed

    def open_csv_file(self, f_name):
        columns = list(self.q_app.data.columns)

        try:
            dd = pd.read_csv(f_name, skiprows=6, skipfooter=1, header=None, names=['eV', '00', '01'])
        except Exception as e:
            print(e)
            return 0, [f_name + ':00', f_name + ':01']

        print(dd)
        if not np.all(dd['01'].isna()):
            for ch in ('00', '01'):
                row = {c: None for c in columns}
                row.update({
                    'DataX': 1E-3 * dd['eV'],
                    'DataY': dd[ch],
                    'DataID': f_name + ':' + ch,
                    'ScreenName': os.path.basename(f_name) + ':' + ch,
                    'Active': True,
                    'Color': next(self.q_app.params['ColorWheel'])
                })

                self.q_app.data.loc[len(self.q_app.data.index)] = row
            return 2, []
        else:
            row = {c: None for c in columns}
            row.update({
                'DataX': 1E-3 * dd['eV'],
                'DataY': dd['00'],
                'DataID': f_name,
                'ScreenName': os.path.basename(f_name),
                'Active': True,
                'Color': next(self.q_app.params['ColorWheel'])
            })

            self.q_app.data.loc[len(self.q_app.data.index)] = row
            return 1, []

    def open_files(self, f_names):
        # TODO: add check if the files are already open
        failed = []
        opened = 0
        for ff in f_names:
            if '.nxs' in ff:
                opn, fld = self.open_nxs_file(ff)
            elif '.raw' in ff:
                opn, fld = self.open_raw_file(ff)
            elif '.csv' in ff:
                opn, fld = self.open_csv_file(ff)
            else:
                opn, fld = 0, ff

            opened += opn
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
