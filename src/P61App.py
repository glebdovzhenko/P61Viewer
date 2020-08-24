"""
src/P61App.py
====================

"""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal
import pandas as pd
import numpy as np
import logging


class P61App(QApplication):
    """
    .. _QApplication: https://doc.qt.io/qtforpython/PySide2/QtWidgets/QApplication.html
    .. _generator: https://wiki.python.org/moin/Generators

    **General:**

    QApplication_ child class that is used for managing the application data.

    This class is a singleton accessible to all application widgets. By convention all widgets store a reference to the
    :code:`P61App` instance as

    .. code-block:: python3

        self.q_app = P61App.instance()


    The widgets use the instance to store and sync data, such as nexus file variables, fit results, etc. Synchronization
    between widgets is done by pyqtSignals. *Important:* it is the widget's responsibility to emit the appropriate
    signal after changing anything in the :code:`P61App.instance()`.

    :code:`P61App.instance().data` **columns and their meaning:**

    :code:`P61App.instance().data` is a :code:`pandas.DataFrame`
    (https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html). Each row of the dataframe
    represents a dataset read from a .nxs file. At the moment .nxs files hold two datasets at
    :code:`'entry/instrument/xspress3/channel00/histogram'` and :code:`'entry/instrument/xspress3/channel01/histogram'`.

    - :code:`'DataX'`: numpy array representing x values on the spectra;
    - :code:`'DataY'`: numpy array representing y values on the spectra;
    - :code:`'DataID'`: unique ID of the dataset built from .nxs file name and field (channel00 / channel01);
    - :code:`'ScreenName'`: name of the dataset shown by the list widgets
    - :code:`'Active'`: boolean status. False means the dataset is not shown on the plot and in the list for fitting.
    - :code:`'Color'`: color of the plot line and screen name on the list
    - :code:`'FitResult'`: :code:`lmfit.ModelResult` object (https://lmfit.github.io/lmfit-py/model.html#lmfit.model.ModelResult)

    :code:`P61App.instance().params` **and their meaning:**

    - :code:`'LmFitModel'`: :code:`lmfit.Model` (https://lmfit.github.io/lmfit-py/model.html#lmfit.model.Model) to fit
      the data in FitWidget;
    - :code:`'SelectedActiveIdx'`: currently selected item's index in ActiveWidget;
    - :code:`'ColorWheel'`: a python generator_ holding the list of colors for plotting;
    - :code:`'ColorWheel2'`: same thing, we just need two of them;

    **Signals and their meaning:**

    - :code:`dataRowsInserted`: when new histograms (rows) are added to the :code:`P61App.instance().data` Dataframe;
    - :code:`dataRowsRemoved`: when histograms (rows) are deleted from the :code:`P61App.instance().data` Dataframe;
    - :code:`dataActiveChanged`: when the :code:`'Active'` status of the rows is changed;

    Three signals above do not just notify the receivers, but also hold the lists of indices of the rows that were
    changed, added or deleted.

    - :code:`selectedIndexChanged`: when the :code:`ActiveListWidget` selection changes (also sends the new
      selected index);
    - :code:`lmFitModelUpdated`: when the :code:`self.params['LmFitModel']` is updated;

    """
    name = 'P61 Viewer'
    version = '0.1.0'

    dataRowsInserted = pyqtSignal(int, int)
    dataRowsRemoved = pyqtSignal(list)
    dataActiveChanged = pyqtSignal(list)
    selectedIndexChanged = pyqtSignal(int)
    peakListChanged = pyqtSignal(list)
    genFitResChanged = pyqtSignal(list)
    bckgInterpChanged = pyqtSignal(list)
    stackedPeaksChanged = pyqtSignal()
    dataModelSetUp = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QApplication.__init__(self, *args, **kwargs)

        # data storage for one-per-dataset items
        self.data = pd.DataFrame(columns=('DataX', 'DataY', 'DeadTime', 'Channel', 'DataID', 'ScreenName', 'Active',
                                          'Color', 'PeakList', 'GeneralFitResult', 'PeakFitResult', 'BckgInterp'))
        self.data_model = None
        self.peak_search_range = None
        self.stacked_peaks = None

        self.logger = logging.getLogger(str(self.__class__))

        # data storage for one-per application items
        self.params = {
            'LmFitModelColors': dict(),
            'SelectedActiveIdx': -1,
            'ColorWheel': self._color_wheel('def'),
            'ColorWheel2': self._color_wheel('def_no_red'),
        }

    def insert_rows(self, position, rows):
        d1, d2 = self.data[:position], self.data[position:]
        insert = pd.DataFrame({col: [None] * rows for col in self.data.columns},
                              index=np.arange(position, position + rows).astype(np.int))
        self.data = pd.concat((d1, insert, d2.set_index(d2.index + rows)))

        self.logger.debug('insert_rows: Inserted %d rows to position %d' %
                          (rows, position))

    def remove_rows(self, position, rows):
        self.data.drop(index=np.arange(position, position + rows).astype(np.int), inplace=True)
        self.data.set_index(np.arange(self.data.shape[0]), inplace=True)

        self.logger.debug('remove_rows: Removed %d rows from position %d' %
                          (rows, position))

    @staticmethod
    def _color_wheel(key):
        ii = 0
        wheels = {
            'def': (0x1f77b4, 0xff7f0e, 0x2ca02c, 0xd62728, 0x9467bd, 0x8c564b, 0xe377c2, 0x7f7f7f, 0xbcbd22, 0x17becf),
            'def_no_red': (0x1f77b4, 0xff7f0e, 0x2ca02c, 0x9467bd, 0x8c564b, 0xe377c2, 0x7f7f7f, 0xbcbd22, 0x17becf),
        }

        wheel = wheels[key]

        while True:
            yield wheel[ii % len(wheel)]
            ii += 1

    def get_active_ids(self):
        return self.data[self.data['Active']].index

    def get_all_ids(self):
        return self.data.index

    def get_selected_idx(self):
        if self.params['SelectedActiveIdx'] == -1:
            return -1
        return self.data[self.data['Active']].index[self.params['SelectedActiveIdx']]

    def get_selected_active_idx(self):
        return self.params['SelectedActiveIdx']

    def set_selected_active_idx(self, val, emit=True):
        self.params['SelectedActiveIdx'] = val
        if emit:
            self.logger.debug('set_selected_active_idx: Emitting selectedIndexChanged(%d)' % (val, ))
            self.selectedIndexChanged.emit(val)

    def get_screen_names(self, only_active=False):
        if only_active:
            return self.data.loc[self.data['Active'], 'ScreenName']
        else:
            return self.data['ScreenName']

    def get_screen_colors(self, only_active=False):
        if only_active:
            return self.data.loc[self.data['Active'], 'Color']
        else:
            return self.data['Color']

    def get_active_status(self):
        return self.data['Active']

    def set_active_status(self, idx, status, emit=True):
        self.data.loc[idx, 'Active'] = bool(status)
        if emit:
            self.logger.debug('set_active_status: Emitting dataActiveChanged([%d])' % (idx, ))
            self.dataActiveChanged.emit([idx])

    def get_selected_screen_name(self):
        return self.data.loc[self.params['SelectedActiveIdx'], 'ScreenName']

    def get_peak_list(self, idx):
        return self.data.loc[idx, 'PeakList']

    def set_peak_list(self, idx, result, emit=True):
        self.data.loc[idx, 'PeakList'] = result
        if emit:
            self.logger.debug('set_peak_list: Emitting peakListChanged([%d])' % (idx, ))
            self.peakListChanged.emit([idx])

    def get_bckg_interp(self, idx):
        return self.data.loc[idx, 'BckgInterp']

    def set_bckg_interp(self, idx, result, emit=True):
        self.data.loc[idx, 'BckgInterp'] = result
        if emit:
            self.logger.debug('set_bckg_interp: Emitting bckgInterpChanged([%d])' % (idx, ))
            self.bckgInterpChanged.emit([idx])

    def get_general_result(self, idx):
        return self.data.loc[idx, 'GeneralFitResult']

    def set_general_result(self, idx, result, emit=True):
        self.data.loc[idx, 'GeneralFitResult'] = result
        if emit:
            self.logger.debug('set_general_result: Emitting genFitResChanged([%d])' % (idx))
            self.genFitResChanged.emit([idx])

    def get_stacked_peaks(self):
        return self.stacked_peaks

    def set_stacked_peaks(self, result, emit=True):
        self.stacked_peaks = result
        if emit:
            self.logger.debug('set_stacked_peaks: Emitting stackedPeaksChanged')
            self.stackedPeaksChanged.emit()
