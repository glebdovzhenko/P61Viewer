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

        self.file_w.file_list_model.dataChanged.connect(self.on_data_changed)

    def on_data_changed(self):
        self.plot_w.clear_line_axes()
        for dd in self.file_w.file_list_model.data_to_plot():
            self.plot_w.plot_line_axes(dd['keV'], dd['Int'])
        self.plot_w.update_line_axes()


if __name__ == '__main__':
    q_app = QApplication(sys.argv)
    app = SpectrumViewer()
    app.show()
    sys.exit(q_app.exec_())
