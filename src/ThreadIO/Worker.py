from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal
import logging


from P61App import P61App


class Worker(QRunnable):

    def __init__(self, fn, args, kwargs):
        super(Worker, self).__init__()
        self.q_app = P61App.instance()
        self.logger = logging.getLogger(str(self.__class__))

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.result = None

        self.threadWorkerException = self.q_app.threadWorkerException
        self.threadWorkerResult = self.q_app.threadWorkerResult
        self.threadWorkerFinished = self.q_app.threadWorkerFinished
        self.threadWorkerStatus = self.q_app.threadWorkerStatus

    @pyqtSlot()
    def run(self) -> None:
        try:
            self.result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.logger.debug('run: Emitting threadWorkerException(%s)' % (str(e),))
            self.threadWorkerException.emit(e)
        else:
            self.threadWorkerResult.emit(self.result)
        finally:
            self.threadWorkerFinished.emit()

