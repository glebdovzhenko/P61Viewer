from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal
import pandas as pd


class P61BApp(QApplication):

    dataRowsAppended = pyqtSignal(int)
    dataRowsRemoved = pyqtSignal(list)
    dataActiveChanged = pyqtSignal(list)
    selectedActiveChanged = pyqtSignal(int)
    plotXYLimChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QApplication.__init__(self, *args, **kwargs)

        self.data = pd.DataFrame(columns=('DataX', 'DataY', 'DataID', 'ScreenName', 'Active', 'Color', 'FitResults'))
        self.selected_active_row = 0
        self.params = {
            'ColorWheel': self._color_wheel(),
            'PlotXLim': (0, 1),
            'PlotYLim': (0, 1),
            'LmFitModel': None
        }

    @staticmethod
    def _color_wheel():
        ii = 0
        wheel = (0x1f77b4, 0xff7f0e, 0x2ca02c, 0xd62728, 0x9467bd, 0x8c564b, 0xe377c2, 0x7f7f7f, 0xbcbd22, 0x17becf)
        while True:
            yield wheel[ii % len(wheel)]
            ii += 1
