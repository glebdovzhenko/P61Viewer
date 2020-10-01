from PyQt5.QtWidgets import QDialog, QAbstractItemView, QGridLayout, QPushButton, QLabel, QComboBox, QProgressDialog, QCheckBox
from PyQt5.Qt import Qt
import copy
import logging

from P61App import P61App
from ThreadIO import Worker
from DatasetManager import DatasetSelector


class FitWorker(Worker):
    def __init__(self, ids, fit_type, bckg, peaks, everything):
        def fn(ids, fit_type, bckg, peaks, everything):
            for ii, (prev_idx, idx) in enumerate(zip(ids[:-1], ids[1:])):
                if self.stop:
                    return
                if fit_type == 2:
                    self.q_app.data.loc[idx, 'GeneralFitResult'] = \
                        copy.deepcopy(self.q_app.data.loc[prev_idx, 'GeneralFitResult'])

                if bckg is not None:
                    bckg(idx=idx)
                if peaks is not None:
                    peaks(idx=idx)
                if everything is not None:
                    everything(idx=idx)

                self.threadWorkerStatus.emit(ii)
            return

        self.stop = False
        super(FitWorker, self).__init__(fn, args=[ids, fit_type, bckg, peaks, everything], kwargs={})

        self.threadWorkerException = self.q_app.fitWorkerException
        self.threadWorkerResult = self.q_app.fitWorkerResult
        self.threadWorkerFinished = self.q_app.fitWorkerFinished
        self.threadWorkerStatus = self.q_app.fitWorkerStatus

    def halt(self):
        self.stop = True


class SeqFitPopUp(QDialog):
    """"""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        self.q_app = P61App.instance()
        self.logger = logging.getLogger(str(self.__class__))

        self.progress = None

        self.current_name = QLabel(parent=self)
        self.combo = QComboBox(parent=self)
        self.combo.addItems(['Do not init', 'Init all from current', 'Sequential from current'])
        self.cb_bckg = QCheckBox('Fit background')
        self.cb_bckg.setChecked(True)
        self.cb_peaks = QCheckBox('Fit peaks')
        self.cb_peaks.setChecked(True)
        self.cb_all = QCheckBox('Fit everything')
        self.btn_ok = QPushButton('Fit', parent=self)
        self.selection_list = DatasetSelector(parent=self)

        self.setWindowTitle('Fit multiple spectra')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.combo, 1, 1, 1, 1)
        layout.addWidget(self.current_name, 2, 1, 1, 1)
        layout.addWidget(self.cb_bckg, 3, 1, 1, 1)
        layout.addWidget(self.cb_peaks, 4, 1, 1, 1)
        layout.addWidget(self.cb_all, 5, 1, 1, 1)
        layout.addWidget(self.btn_ok, 6, 1, 1, 1)
        layout.addWidget(self.selection_list, 1, 2, 6, 1)

        self.btn_ok.clicked.connect(self.on_btn_ok)
        self.combo.currentIndexChanged.connect(self.on_combo_index_change)

    def on_tw_finished(self):
        self.logger.debug('on_tw_finished: Handling FitOpenWorker.threadWorkerFinished')
        if self.progress is not None:
            self.progress.close()
            self.progress = None
            self.close()

    def on_tw_exception(self, e):
        self.logger.debug('on_tw_exception: Handling FitOpenWorker.threadWorkerException')
        if self.progress is not None:
            self.progress.close()
            self.progress = None

    def on_combo_index_change(self):
        if self.q_app.get_selected_idx() == -1:
            return
        if self.combo.currentIndex() in (1, 2):
            self.current_name.setText(self.q_app.get_selected_screen_name())
        else:
            self.current_name.setText('')

    def on_btn_ok(self):
        if self.q_app.get_selected_idx() == -1:
            self.close()
            return

        fit_ids = [k for k in self.selection_list.proxy.selected if self.selection_list.proxy.selected[k]]
        fit_type = self.combo.currentIndex()

        if fit_type == 1:
            self.q_app.data.loc[fit_ids, 'GeneralFitResult'] = [self.q_app.get_general_result(
                self.q_app.get_selected_idx())] * len(fit_ids)

        fit_ids = [self.q_app.get_selected_idx()] + fit_ids

        self.progress = QProgressDialog("Sequential refinement", "Cancel", 0, len(fit_ids))
        self.progress.setWindowModality(Qt.ApplicationModal)

        fw = FitWorker(fit_ids, fit_type,
                       self.parent().on_bckg_fit_btn if self.cb_bckg.isChecked() else None,
                       self.parent().on_peak_fit_btn if self.cb_peaks.isChecked() else None,
                       self.parent().on_fit_btn if self.cb_all.isChecked() else None)

        fw.threadWorkerException.connect(self.on_tw_exception)
        fw.threadWorkerFinished.connect(self.on_tw_finished)
        fw.threadWorkerStatus.connect(self.progress.setValue)

        cb = QPushButton('Cancel')
        cb.clicked.connect(lambda *args: fw.halt())
        self.progress.setCancelButton(cb)
        self.progress.show()
        self.q_app.thread_pool.start(fw)

        # TODO: add cancel functionality
        # progress = QProgressDialog("Batch Fit", "Cancel", 0, len(fit_ids))
        # progress.setWindowModality(Qt.WindowModal)
        # for ii, (prev_idx, idx) in enumerate(zip([self.q_app.get_selected_idx()] + fit_ids[:-1], fit_ids)):
        #     progress.setValue(ii)
        #     if fit_type == 2:
        #         self.q_app.data.loc[idx, 'GeneralFitResult'] = \
        #             copy.deepcopy(self.q_app.data.loc[prev_idx, 'GeneralFitResult'])
        #
        #     if self.cb_bckg.isChecked():
        #         self.parent().on_bckg_fit_btn(idx=idx)
        #     if self.cb_peaks.isChecked():
        #         self.parent().on_peak_fit_btn(idx=idx)
        #     if self.cb_all.isChecked():
        #         self.parent().on_fit_btn(idx=idx)
        # progress.setValue(len(fit_ids))
