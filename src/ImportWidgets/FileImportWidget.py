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

        self.colorwheel = self._colorwheel()

    @staticmethod
    def _colorwheel():
        ii = 0
        wheel = (0x1f77b4, 0xff7f0e, 0x2ca02c, 0xd62728, 0x9467bd, 0x8c564b, 0xe377c2, 0x7f7f7f, 0xbcbd22, 0x17becf)
        while True:
            yield wheel[ii % len(wheel)]
            ii += 1

    def open_files(self, f_names):
        # TODO: add check if the files are already open
        ch0, ch1 = 'entry/instrument/xspress3/channel00/histogram', \
                   'entry/instrument/xspress3/channel01/histogram'

        failed = []
        for ff in f_names:
            for channel in (ch0, ch1):
                try:
                    with h5py.File(ff, 'r') as f:
                        frames = np.sum(f[channel], axis=0)
                        frames[:20] = 0.0
                        frames[-1] = 0.0
                        kev = (np.arange(frames.shape[0]) + 0.5) * self.kev_per_bin

                        self.q_app.data.loc[len(self.q_app.data.index) + 1] = {
                                'DataX': kev,
                                'DataY': frames,
                                'DataID': ff + '::' + channel,
                                'ScreenName': os.path.basename(ff) + ':' + channel[-2:],
                                'Active': True,
                                'Color': next(self.colorwheel)
                            }

                except Exception as e:
                    print(e)
                    failed.append(ff + '::' + channel)

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
    sys.exit(q_app.exec())
