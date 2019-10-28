from PyQt5.QtWidgets import QWidget, QErrorMessage
import h5py
import numpy as np
import os

from P61BApp import P61BApp


class FileImportWidget(QWidget):
    """"""
    kev_per_bin = 5E-2

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61BApp.instance()

    def open_files(self, f_names):
        # TODO: add check if the files are already open
        ch0, ch1 = 'entry/instrument/xspress3/channel00/histogram', \
                   'entry/instrument/xspress3/channel01/histogram'

        columns = list(self.q_app.data.columns)

        failed = []
        for ff in f_names:
            for ii, channel in enumerate((ch0, ch1)):
                try:
                    with h5py.File(ff, 'r') as f:
                        frames = np.sum(f[channel], axis=0)
                        frames[:20] = 0.0
                        frames[-1] = 0.0
                        kev = (np.arange(frames.shape[0]) + 0.5) * self.kev_per_bin

                        row = {c: None for c in columns}
                        row.update({
                                'DataX': kev,
                                'DataY': frames,
                                'DataID': ff + ':' + channel,
                                'ScreenName': os.path.basename(ff) + ':' + '%02d' % ii,
                                'Active': True,
                                'Color': next(self.q_app.params['ColorWheel'])
                            })

                        self.q_app.data.loc[len(self.q_app.data.index)] = row

                except Exception as e:
                    print(e)
                    failed.append(ff + '::' + channel)

        self.q_app.dataRowsAppended.emit(len(f_names) * 2 - len(failed))

        if failed:
            msg = QErrorMessage()
            msg.showMessage('Could not open files:\n' + '\n'.join(failed))
            msg.exec_()


if __name__ == '__main__':
    import sys
    q_app = P61BApp(sys.argv)
    wg = FileImportWidget()
    wg.open_files(
        ['/Users/glebdovzhenko/Dropbox/PycharmProjects/P61BViewer/test_files/collected/Co57_2019-09-30_09-10-30_.nxs',
         '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61BViewer/test_files/collected/Co57_2019-09-30_09-27-11_.nxs',
         '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61BViewer/test_files/collected/Co57_2019-09-30_09-43-51_.nxs',
         '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61BViewer/test_files/collected/Co57_2019-09-30_10-00-32_.nxs',
         '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61BViewer/test_files/collected/Co57_2019-09-30_10-17-13_.nxs'])
    print(q_app.data)
    print(q_app.data.iloc[0])
    sys.exit(q_app.exec())
