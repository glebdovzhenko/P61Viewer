from PyQt5.QtWidgets import QApplication

from P61BViewerProject import P61BViewerProject


class P61BApp(QApplication):
    def __init__(self, *args, **kwargs):
        QApplication.__init__(self, *args, **kwargs)

        self.project = P61BViewerProject()