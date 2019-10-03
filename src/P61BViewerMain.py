from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QWidget
import sys
from FileListWidget import FileListWidget
from PlotWidget import PlotWidget


class P61BViewer(QMainWindow):

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
        for line in self.file_w.file_list_model.data_to_plot():
            self.plot_w.axes_add_line(line)
        self.plot_w.update_line_axes(autoscale=False)


if __name__ == '__main__':
    q_app = QApplication(sys.argv)
    app = P61BViewer()
    app.show()
    sys.exit(q_app.exec_())
