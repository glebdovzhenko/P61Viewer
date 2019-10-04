from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QWidget, QTabWidget
import sys
from FileListWidget import FileListWidget
from PlotWidget import PlotWidget
from PeakFitWidget import PeakFitWidget


class P61BViewer(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent=parent)

        # initiate self
        self.resize(1200, 800)
        self.setWindowTitle('P61B Spectrum Viewer')

        # initiate widgets
        self.cw = QTabWidget(parent=self)
        self.setCentralWidget(self.cw)
        view_tab = QWidget()

        self.file_w = FileListWidget(parent=self)
        self.view_plot_w = PlotWidget(parent=self)
        self.fit_plot_w = PlotWidget(parent=self, controls=False)
        self.peak_f_w = PeakFitWidget(parent=self)

        # set up layouts
        view_layout = QHBoxLayout()
        view_tab.setLayout(view_layout)
        view_layout.addWidget(self.view_plot_w, 3)
        view_layout.addWidget(self.file_w, 1)

        fit_tab = QWidget()
        fit_layout = QHBoxLayout()
        fit_tab.setLayout(fit_layout)
        fit_layout.addWidget(self.peak_f_w, 1)
        fit_layout.addWidget(self.fit_plot_w, 3)

        self.cw.addTab(view_tab, 'View')
        self.cw.addTab(fit_tab, 'Fit')

        # signal handlers
        self.file_w.file_list_model.dataChanged.connect(self.on_data_changed)
        self.file_w.file_list_model.filesAdded.connect(self.on_files_added)

    def on_data_changed(self):
        self.view_plot_w.clear_line_axes()
        for line in self.file_w.file_list_model.data_to_plot():
            self.view_plot_w.axes_add_line(line)
        self.view_plot_w.update_line_axes(autoscale=False)

    def on_files_added(self):
        self.view_plot_w.update_line_axes()


if __name__ == '__main__':
    q_app = QApplication(sys.argv)
    app = P61BViewer()
    app.show()
    sys.exit(q_app.exec_())
