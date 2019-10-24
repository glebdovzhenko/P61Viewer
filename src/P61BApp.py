from PyQt5.QtWidgets import QApplication
import pandas as pd

from P61BViewerProject import P61BViewerProject


class P61BApp(QApplication):
    def __init__(self, *args, **kwargs):
        QApplication.__init__(self, *args, **kwargs)

        self.project = P61BViewerProject()
        self.data = pd.DataFrame(columns=('DataX', 'DataY', 'DataID', 'ScreenName', 'Active', 'Color'))
