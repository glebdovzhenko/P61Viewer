from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QWidget
import sys
from src.FileListWidget import FileListWidget
from src.PlotWidget import PlotWidget


class SpectrumViewer(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent=parent)

        self.cw = QWidget(parent=self)
        self.file_w = FileListWidget(parent=self)
        self.plot_w = PlotWidget(parent=self)

        layout = QHBoxLayout()
        layout.addWidget(self.plot_w)
        layout.addWidget(self.file_w)
        self.cw.setLayout(layout)

        self.setCentralWidget(self.cw)

        self.file_w.table_model.dataChanged.connect(self.on_data_changed)

    def on_data_changed(self):
        self.plot_w._line_ax.clear()
        for dd in self.file_w.table_model.data_to_plot():
            self.plot_w._line_ax.plot(dd['keV'], dd['Int'])
        self.plot_w._line_ax.figure.canvas.draw()


if __name__ == '__main__':
    qapp = QApplication(sys.argv)
    app = SpectrumViewer()
    app.show()
    sys.exit(qapp.exec_())
