"""
src/P61App.py
====================

Support.
"""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal
import pandas as pd


class P61App(QApplication):

    dataRowsAppended = pyqtSignal(int)
    dataRowsRemoved = pyqtSignal(list)
    dataActiveChanged = pyqtSignal(list)
    selectedIndexChanged = pyqtSignal(int)
    plotXYLimChanged = pyqtSignal()
    lmFitModelUpdated = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QApplication.__init__(self, *args, **kwargs)

        self.data = pd.DataFrame(columns=('DataX', 'DataY', 'DataID', 'ScreenName', 'Active', 'Color', 'FitResult'))
        self.params = {
            'LmFitModel': None,
            'SelectedIndex': -1,
            'ColorWheel': self._color_wheel('def'),
            'ColorWheel2': self._color_wheel('def_no_red'),
            'PlotXLim': (0, 1),
            'PlotYLim': (0, 1),
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
