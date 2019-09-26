from PyQt5.QtWidgets import QWidget, QApplication, QAbstractItemView, QPushButton, QGridLayout, QFileDialog, \
    QErrorMessage, QListView, QCheckBox
from PyQt5.QtCore import QSize, Qt

from src.FileListModel import FileListModel


class FileListWidget(QWidget):
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)

        # List model - view
        self.file_list_model = FileListModel()
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
        self.file_list_view.selectionModel().selectionChanged.connect(self.check_box_update)
        self.file_list_model.dataChanged.connect(self.check_box_update)

    def bminus_onclick(self):
        rows = [i.row() for i in self.file_list_view.selectedIndexes()]
        for i in sorted(rows, reverse=True):
            self.file_list_model.removeRow(i)

    def bplus_onclick(self):
        files, _ = \
            QFileDialog.getOpenFileNames(self, 'Add spectra',
                                         '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/pwdr_h5',
                                         'All Files (*);;HDF5 files (*.h5);;NEXUS files (*.nxs)',
                                         options=QFileDialog.Options())

        failed = self.file_list_model.append_files(files)

        if failed:
            msg = QErrorMessage()
            msg.showMessage('Could not open files:\n' + '\n'.join(failed))
            msg.exec_()

    def check_box_on_click(self):
        self.check_box.setTristate(False)

        self.file_list_model.update_plot_show(self.file_list_view.selectionModel().selectedIndexes(),
                                              bool(self.check_box.checkState()))

    def check_box_update(self):
        status = self.file_list_model.get_plot_show(self.file_list_view.selectionModel().selectedIndexes())

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
