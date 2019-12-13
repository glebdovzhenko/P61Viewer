"""
src/P61App.py
====================

"""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
import pandas as pd


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
    - :code:`'SelectedIndex'`: currently selected item's index in ActiveWidget;
    - :code:`'ColorWheel'`: a python generator_ holding the list of colors for plotting;
    - :code:`'ColorWheel2'`: same thing, we just need two of them;

    **Signals and their meaning:**

    - :code:`dataRowsAppended`: when new histograms (rows) are added to the :code:`P61App.instance().data` Dataframe;
    - :code:`dataRowsRemoved`: when histograms (rows) are deleted from the :code:`P61App.instance().data` Dataframe;
    - :code:`dataActiveChanged`: when the :code:`'Active'` status of the rows is changed;

    Three signals above do not just notify the receivers, but also hold the lists of indices of the rows that were
    changed, added or deleted.

    - :code:`selectedIndexChanged`: when the :code:`ActiveListWidget` selection changes (also sends the new
      selected index);
    - :code:`lmFitModelUpdated`: when the :code:`self.params['LmFitModel']` is updated;

    """
    name = 'P61 Viewer'
    version = '0.0.3'

    dataRowsAppended = pyqtSignal(int)
    dataRowsRemoved = pyqtSignal(list)
    dataActiveChanged = pyqtSignal(list)
    selectedIndexChanged = pyqtSignal(int)
    dataFitChanged = pyqtSignal(list)
    lmFitModelUpdated = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QApplication.__init__(self, *args, **kwargs)

        self.data = pd.DataFrame(columns=('DataX', 'DataY', 'DataID', 'ScreenName', 'Active', 'Color', 'FitResult'))
        # self.setWindowIcon(QIcon('../img/icon.png'))
        self.params = {
            'LmFitModel': None,
            'SelectedIndex': -1,
            'ColorWheel': self._color_wheel('def'),
            'ColorWheel2': self._color_wheel('def_no_red'),
        }

    @staticmethod
    def _color_wheel(key):
        ii = 0
        wheels = {
            'def': (0x1f77b4, 0xff7f0e, 0x2ca02c, 0xd62728, 0x9467bd, 0x8c564b, 0xe377c2, 0x7f7f7f, 0xbcbd22, 0x17becf),
            'def_no_red': (0x1f77b4, 0xff7f0e, 0x2ca02c, 0x9467bd, 0x8c564b, 0xe377c2, 0x7f7f7f, 0xbcbd22, 0x17becf),
            'tab20b': (0x393b79, 0x5254a3, 0x6b6ecf, 0x9c9ede, 0x637939, 0x8ca252, 0xb5cf6b, 0xcedb9c, 0x8c6d31,
                       0xbd9e39, 0xe7ba52, 0xe7cb94, 0x843c39, 0xad494a, 0xd6616b, 0xe7969c, 0x7b4173, 0xa55194,
                       0xce6dbd, 0xde9ed6),
            'tab20c': (0x3182bd, 0x6baed6, 0x9ecae1, 0xc6dbef, 0xe6550d, 0xfd8d3c, 0xfdae6b, 0xfdd0a2, 0x31a354,
                       0x74c476, 0xa1d99b, 0xc7e9c0, 0x756bb1, 0x9e9ac8, 0xbcbddc, 0xdadaeb, 0x636363, 0x969696,
                       0xbdbdbd, 0xd9d9d9)
        }

        wheel = wheels[key]

        while True:
            yield wheel[ii % len(wheel)]
            ii += 1
