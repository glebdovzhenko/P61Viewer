from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QTableView, QAbstractItemView, QPushButton, QCheckBox, QGridLayout, QFileDialog, \
    QErrorMessage, QMessageBox, QHeaderView, QProgressDialog
import os
import pandas as pd
import logging

from P61App import P61App
from ThreadIO import Worker
from DatasetIO import DatasetReaders


class FileOpenWorker(Worker):
    def __init__(self, files):
        def fn(fs):
            failed, opened = [], pd.DataFrame(columns=self.q_app.data.columns)
            for ii, file in enumerate(fs):
                if self.stop:
                    break
                try:
                    for reader in DatasetReaders:
                        if reader().validate(file):
                            opened = pd.concat((opened, reader().read(file)), ignore_index=True)
                            break
                    else:
                        failed.append(file)
                except Exception as e:
                    self.logger.info(str(e))
                    failed.append(file)

                self.threadWorkerStatus.emit(ii)
            return failed, opened

        self.stop = False

        super(FileOpenWorker, self).__init__(fn, args=[files], kwargs={})

        self.threadWorkerException = self.q_app.foWorkerException
        self.threadWorkerResult = self.q_app.foWorkerResult
        self.threadWorkerFinished = self.q_app.foWorkerFinished
        self.threadWorkerStatus = self.q_app.foWorkerStatus

    def halt(self):
        self.stop = True


class DatasetManager(QWidget):
    def __init__(self, parent=None, *args):
        QWidget.__init__(self, parent, *args)
        self.q_app = P61App.instance()
        self.logger = logging.getLogger(str(self.__class__))
        self.progress = None

        self.view = QTableView()
        self.view.setModel(self.q_app.data_model)
        self.view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSortingEnabled(True)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.view.horizontalHeader().setStretchLastSection(True)

        # buttons and checkbox
        self.bplus = QPushButton('+')
        self.bminus = QPushButton('-')
        self.checkbox = QCheckBox('')
        self.bexport = QPushButton('Export')
        self.checkbox.setTristate(False)
        self.bplus.setFixedSize(QSize(51, 32))
        self.bminus.setFixedSize(QSize(51, 32))
        self.bplus.clicked.connect(self.bplus_onclick)
        self.bminus.clicked.connect(self.bminus_onclick)
        self.bexport.clicked.connect(self.bexport_onclick)
        self.checkbox.clicked.connect(self.checkbox_onclick)

        # layouts
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.checkbox, 1, 1, 1, 1)
        layout.addWidget(self.bplus, 1, 3, 1, 1)
        layout.addWidget(self.bminus, 1, 4, 1, 1)
        layout.addWidget(self.view, 2, 1, 1, 4)
        layout.addWidget(self.bexport, 3, 3, 1, 2)

        # signals and handlers
        self.view.selectionModel().selectionChanged.connect(self.checkbox_update)
        self.q_app.dataActiveChanged.connect(self.on_data_ac)

    def on_data_ac(self, rows):
        self.logger.debug('on_data_ac: Handling dataActiveChanged(%s)' % (str(rows), ))
        self.checkbox_update()

    def bplus_onclick(self):
        if self.progress is not None:
            return
        fd = QFileDialog()
        files, _ = fd.getOpenFileNames(
            self,
            'Add spectra',
            '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/pwdr_h5',
            'All Files (*);;NEXUS files (*.nxs)',
            options=QFileDialog.Options()
        )

        self.progress = QProgressDialog("Opening files", "Cancel", 0, len(files))
        fw = FileOpenWorker(files)
        fw.threadWorkerException.connect(self.on_tw_exception)
        fw.threadWorkerResult.connect(self.on_tw_result)
        fw.threadWorkerFinished.connect(self.on_tw_finished)
        fw.threadWorkerStatus.connect(self.progress.setValue)

        cb = QPushButton('Cancel')
        cb.clicked.connect(lambda *args: fw.halt())
        self.progress.setCancelButton(cb)
        self.progress.show()
        self.q_app.thread_pool.start(fw)

    def on_tw_finished(self):
        self.logger.debug('on_tw_finished: Handling FileOpenWorker.threadWorkerFinished')
        if self.progress is not None:
            self.progress.close()
            self.progress = None

    def on_tw_exception(self, e):
        self.logger.debug('on_tw_exception: Handling FileOpenWorker.threadWorkerException')
        if self.progress is not None:
            self.progress.close()
            self.progress = None

    def on_tw_result(self, result):
        self.logger.debug('on_tw_result: Handling FileOpenWorker.threadWorkerResult')
        failed, opened = result
        self.q_app.data_model.insertRows(0, opened.shape[0])
        self.q_app.data[0:opened.shape[0]] = opened
        self.q_app.data_model.dataChanged.emit(
            self.q_app.data_model.index(0, 0),
            self.q_app.data_model.index(opened.shape[0], self.q_app.data_model.columnCount())
        )

        self.logger.debug('on_tw_result: Emitting dataRowsInserted(%d, %d)' % (0, opened.shape[0]))
        self.q_app.dataRowsInserted.emit(0, opened.shape[0])

        if failed:
            msg = QErrorMessage()
            msg.showMessage('Could not open files:\n' + '\n'.join(failed))
            msg.exec_()

    @staticmethod
    def to_consecutive(lst):
        """
        Transforms a list of indices to a list of pairs (index, amount of consecutive indices after it)
        :param lst:
        :return:
        """
        if len(lst) == 1:
            return [(lst[0], 1), ]

        i1, i2 = 0, 1
        result = []
        while i2 < len(lst):
            if lst[i2] - lst[i1] == i2 - i1:
                i2 += 1
            else:
                result.append((lst[i1], i2 - i1))
                i1 = i2
                i2 += 1
        result.append((lst[i1], i2 - i1))
        return reversed(result)

    def bminus_onclick(self):
        if self.progress is not None:
            return
        rows = list(set(idx.row() for idx in self.view.selectedIndexes()))
        for position, amount in self.to_consecutive(sorted(rows)):
            self.q_app.data_model.removeRows(position, amount)
        self.logger.debug('bminus_onclick: Emitting dataRowsRemoved(%s)' % (str(rows), ))
        self.q_app.dataRowsRemoved.emit(rows)

    def bexport_onclick(self):
        if self.progress is not None:
            return
        fd = QFileDialog()
        fd.setOption(fd.ShowDirsOnly, True)
        dirname = fd.getExistingDirectory(self, caption='Export spectra to')

        rows = [idx.row() for idx in self.view.selectedIndexes()]
        rows = sorted(set(rows))

        names = self.q_app.data.loc[rows, 'ScreenName'].apply(lambda x: x.replace(':', '_').replace('.', '_') + '.csv')
        overlap = set(os.listdir(dirname)) & set(names)
        ret = QMessageBox.Ok

        if overlap:
            msg = QMessageBox(self)
            msg.setText('Warning! The following files will be overwritten')
            msg.setInformativeText('\n'.join(sorted(overlap)))
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = msg.exec()

        if ret == QMessageBox.Ok:
            for ii in rows:
                data = self.q_app.data.loc[ii, ['DataX', 'DataY', 'ScreenName']]
                f_name = data['ScreenName'].replace(':', '_').replace('.', '_') + '.csv'
                data = pd.DataFrame(data={'eV': 1E3 * data['DataX'], 'counts': data['DataY']})
                data = data[['eV', 'counts']]
                data.to_csv(os.path.join(dirname, f_name), header=True, index=False)

    def checkbox_onclick(self):
        self.checkbox.setTristate(False)
        rows = sorted(set([idx.row() for idx in self.view.selectedIndexes()]))
        for row in rows:
            self.q_app.set_active_status(row, bool(self.checkbox.checkState()), emit=False)

        self.q_app.data_model.dataChanged.emit(
            self.q_app.data_model.index(min(rows), 0),
            self.q_app.data_model.index(max(rows), 0),
        )

        self.logger.debug('checkbox_onclick: Emitting dataActiveChanged(%s)' % (str(rows),))
        self.q_app.dataActiveChanged.emit(rows)

    def checkbox_update(self):
        rows = [idx.row() for idx in self.view.selectedIndexes()]
        status = self.q_app.get_active_status()
        status = status[rows]

        if all(status):
            self.checkbox.setCheckState(Qt.Checked)
        elif not any(status):
            self.checkbox.setCheckState(Qt.Unchecked)
        else:
            self.checkbox.setCheckState(Qt.PartiallyChecked)
