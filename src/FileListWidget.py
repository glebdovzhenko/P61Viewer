from PyQt5.QtWidgets import QWidget, QApplication, QAbstractItemView, QPushButton, QGridLayout, QFileDialog, \
    QErrorMessage, QListView
from PyQt5.QtCore import QSize

from src.SpectrumFileData import SpectrumFileData
from src.FileListModel import FileListModel


class FileListWidget(QWidget):
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)

        # List model - view
        self.file_list_model = FileListModel([])
        self.file_list_view = QListView()
        self.file_list_view.setModel(self.file_list_model)

        # buttons
        bplus = QPushButton('+')
        bminus = QPushButton('-')
        bplus.setFixedSize(QSize(51, 32))
        bminus.setFixedSize(QSize(51, 32))
        bplus.clicked.connect(self.bplus_onclick)
        bminus.clicked.connect(self.bminus_onclick)

        # properties
        self.file_list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # layouts
        layout = QGridLayout()
        layout.addWidget(bplus, 1, 2, 1, 1)
        layout.addWidget(bminus, 1, 3, 1, 1)
        layout.addWidget(self.file_list_view, 2, 1, 1, 3)
        self.setLayout(layout)

    def bminus_onclick(self):
        rows = [i.row() for i in self.file_list_view.selectedIndexes()]
        for i in sorted(rows, reverse=True):
            self.file_list_model.removeRow(i)
        # TODO: is this safe? rows min(rows) and max(rows) might not exist at this point
        self.file_list_model.dataChanged.emit(self.file_list_model.index(min(rows), 0),
                                              self.file_list_model.index(max(rows), 0))

    def bplus_onclick(self):
        files, _ = \
            QFileDialog.getOpenFileNames(self, 'Add spectra',
                                         '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/pwdr_h5',
                                         'All Files (*);;HDF5 files (*.h5)', options=QFileDialog.Options())
        files = [ff for ff in files if ff not in self.file_list_model.get_names()]

        success, failed = [], []
        for ff in files:
            tmp = SpectrumFileData('')
            if tmp.init_from_h5(ff):
                success.append(tmp)
            else:
                failed.append(ff)

        if failed:
            msg = QErrorMessage()
            msg.showMessage('Could not open files:\n' + '\n'.join(failed))
            msg.exec_()

        self.file_list_model.append_files(success)


if __name__ == '__main__':
    import sys
    qapp = QApplication(sys.argv)
    app = FileListWidget()
    app.show()
    sys.exit(qapp.exec_())
