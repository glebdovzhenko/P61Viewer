from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QWidget
import sys
from src.FileListWidget import FileListWidget
from src.PlotWidget import PlotWidget


class SpectrumViewer(QMainWindow):
    color_cycle = ('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf')

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent=parent)

        # initiate self
        self.resize(1200, 800)
        self.setWindowTitle('P61 Spectrum Viewer')

        # initiate widgets
        self.cw = QWidget(parent=self)
        self.setCentralWidget(self.cw)
        self.file_w = FileListWidget(parent=self)
        self.plot_w = PlotWidget(parent=self)

        # set up layouts
        layout = QHBoxLayout()
        self.cw.setLayout(layout)
        layout.addWidget(self.plot_w)
        layout.addWidget(self.file_w)

        # signal handlers
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
