from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QTableView, QAbstractItemView, QPushButton, QCheckBox, QGridLayout, QFileDialog, \
    QErrorMessage, QMessageBox
import os
import pandas as pd
import logging

from P61App import P61App
from DatasetIO import DatasetReaders


class DataSetStorageModel(QAbstractTableModel):
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.q_app = P61App.instance()
        self.logger = logging.getLogger(str(self.__class__))

        self.c_names = ['Name', u'💀⏱', u'χ²']

        self.q_app.data_model = self
        self.logger.debug('__init__: Emitting dataModelSetUp')
        self.q_app.dataModelSetUp.emit()

        self.q_app.genFitResChanged.connect(self.on_gen_fit_changed)

    def on_gen_fit_changed(self, rows):
        self.logger.debug('on_gen_fit_changed: Handling genFitResChanged(%s)' % (str(rows),))
        if rows:
            self.dataChanged.emit(
                self.index(min(rows), 2),
                self.index(max(rows), 2)
            )

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    def rowCount(self, parent=None, *args, **kwargs):
        return self.q_app.data.shape[0]

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.c_names[section]

    def data(self, ii: QModelIndex, role=None):
        if not ii.isValid():
            return None

        item_row = self.q_app.data.loc[ii.row()]

        if ii.column() == 0:
            if role == Qt.DisplayRole:
                return item_row['ScreenName']
            elif role == Qt.CheckStateRole:
                return Qt.Checked if item_row['Active'] else Qt.Unchecked
            elif role == Qt.ForegroundRole:
                if item_row['Active']:
                    return QColor(item_row['Color'])
                else:
                    return QColor('Black')
            else:
                return None
        elif ii.column() == 1:
            if role == Qt.DisplayRole:
                return item_row['DeadTime']
            else:
                return None
        elif ii.column() == 2:
            if role == Qt.DisplayRole:
                if item_row['GeneralFitResult'] is not None:
                    if item_row['GeneralFitResult'].chisqr is not None:
                        return '%.01f' % item_row['GeneralFitResult'].chisqr
                    else:
                        return None
                else:
                    return None
            else:
                return None
        else:
            return None

    def flags(self, ii: QModelIndex):
        if not ii.isValid():
            return 0

        result = super(QAbstractTableModel, self).flags(ii)

        if ii.column() == 0:
            result |= Qt.ItemIsUserCheckable

        return result

    def insertRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginInsertRows(parent, position, position + rows - 1)
        self.q_app.insert_rows(position, rows)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginRemoveRows(parent, position, position + rows - 1)
        self.q_app.remove_rows(position, rows)
        self.endRemoveRows()
        return True

    def setData(self, ii: QModelIndex, value, role=None):
        if ii.column() == 0 and role == Qt.CheckStateRole:
            self.q_app.set_active_status(ii.row(), bool(value))
            self.dataChanged.emit(ii, ii)
            return True
        else:
            return False


class DatasetManager(QWidget):
    def __init__(self, parent=None, *args):
        QWidget.__init__(self, parent, *args)
        self.q_app = P61App.instance()
        self.logger = logging.getLogger(str(self.__class__))

        self.view = QTableView()
        self.model = DataSetStorageModel()
        self.view.setModel(self.model)
        self.view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.view.setSelectionBehavior(QTableView.SelectRows)

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
        fd = QFileDialog()
        files, _ = fd.getOpenFileNames(
            self,
            'Add spectra',
            '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/pwdr_h5',
            'All Files (*);;NEXUS files (*.nxs)',
            options=QFileDialog.Options()
        )

        failed, opened = [], pd.DataFrame(columns=self.q_app.data.columns)
        for file in files:
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

        # opened = opened.astype({'DeadTime': })
        self.model.insertRows(0, opened.shape[0])
        self.q_app.data[0:opened.shape[0]] = opened
        self.model.dataChanged.emit(
            self.model.index(0, 0),
            self.model.index(opened.shape[0], self.model.columnCount())
        )

        self.logger.debug('bplus_onclick: Emitting dataRowsInserted(%d, %d)' % (0, opened.shape[0]))
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
        rows = list(set(idx.row() for idx in self.view.selectedIndexes()))
        for position, amount in self.to_consecutive(sorted(rows)):
            self.model.removeRows(position, amount)
        self.logger.debug('bminus_onclick: Emitting dataRowsRemoved(%s)' % (str(rows), ))
        self.q_app.dataRowsRemoved.emit(rows)

    def bexport_onclick(self):
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

        self.model.dataChanged.emit(
            self.model.index(min(rows), 0),
            self.model.index(max(rows), 0),
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
