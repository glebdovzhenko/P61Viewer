from PyQt5.QtWidgets import QWidget, QApplication, QAbstractItemView, QPushButton, QGridLayout, QFileDialog, \
    QErrorMessage, QListView, QCheckBox
from PyQt5.QtCore import QSize, Qt

from src.SpectrumFileData import SpectrumFileData
from src.FileListModel import FileListModel


class FileListWidget(QWidget):
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)

        # List model - view
        self.file_list_model = FileListModel([])
        self.file_list_view = QListView()
        self.file_list_view.setModel(self.file_list_model)

        # buttons and checkboxes
        bplus = QPushButton('+')
        bminus = QPushButton('-')
        self.check_box = QCheckBox(' ')
        self.check_box.setTristate(False)
        bplus.setFixedSize(QSize(51, 32))
        bminus.setFixedSize(QSize(51, 32))
        bplus.clicked.connect(self.bplus_onclick)
        bminus.clicked.connect(self.bminus_onclick)
        self.check_box.clicked.connect(self.check_box_on_click)

        # properties
        self.file_list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # layouts
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.check_box, 1, 1, 1, 1)
        layout.addWidget(bplus, 1, 3, 1, 1)
        layout.addWidget(bminus, 1, 4, 1, 1)
        layout.addWidget(self.file_list_view, 2, 1, 1, 4)

        # signal handlers
        self.file_list_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.file_list_model.dataChanged.connect(self.on_selection_changed)

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
                                         'All Files (*);;HDF5 files (*.h5);;NEXUS files (*.nxs)',
                                         options=QFileDialog.Options())
        files = [ff for ff in files if ff not in self.file_list_model.get_names()]

        success, failed = [], []
        # for ff in files:
        #     tmp = SpectrumFileData('')
        #     if tmp.init_from_h5(ff):
        #         success.append(tmp)
        #     else:
        #         failed.append(ff)

        for ff in files:
            tmp0, tmp1 = SpectrumFileData(''), SpectrumFileData('')
            if tmp0.init_from_nexus(ff, 'channel00') and tmp1.init_from_nexus(ff, 'channel01'):
                success.extend([tmp0, tmp1])
            else:
                failed.append(ff)

        if failed:
            msg = QErrorMessage()
            msg.showMessage('Could not open files:\n' + '\n'.join(failed))
            msg.exec_()

        self.file_list_model.append_files(success)

    def check_box_on_click(self):
        self.check_box.setTristate(False)
        rows = [idx.row() for idx in self.file_list_view.selectionModel().selectedIndexes()]

        for row in rows:
            self.file_list_model.file_data_list[row].set_show_status(bool(self.check_box.checkState()))
        if rows:
            self.file_list_model.dataChanged.emit(self.file_list_model.index(min(rows)),
                                                  self.file_list_model.index(max(rows)))

    def on_selection_changed(self):
        status = [bool(self.file_list_model.data(idx, role=Qt.CheckStateRole))
                  for idx in self.file_list_view.selectionModel().selectedIndexes()]

        if all(status):
            self.check_box.setCheckState(Qt.Checked)
        elif not any(status):
            self.check_box.setCheckState(Qt.Unchecked)
        else:
            self.check_box.setCheckState(Qt.PartiallyChecked)


if __name__ == '__main__':
    import sys
    q_app = QApplication(sys.argv)
    app = FileListWidget()
    app.show()
    sys.exit(q_app.exec_())
