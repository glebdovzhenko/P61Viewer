from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QTabWidget, QHBoxLayout

from P61App import P61App

from PlotWidgets import PAItemView
from ListWidgets import ActiveListWidget


class PAPlotWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.q_app = P61App.instance()

        self.tabs = QTabWidget(parent=self)
        self.item_view_tab = QWidget(parent=self.tabs)
        self.heat_map_tab = QWidget(parent=self.tabs)

        iv_layout = QHBoxLayout()
        self.item_view_tab.setLayout(iv_layout)
        iv_layout.addWidget(ActiveListWidget(parent=self.item_view_tab), 1)
        iv_layout.addWidget(PAItemView(parent=self.item_view_tab), 3)

        self.tabs.addTab(self.item_view_tab, 'Item View')
        self.tabs.addTab(self.heat_map_tab, 'Heat Map')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.tabs)


if __name__ == '__main__':
    import sys

    q_app = P61App(sys.argv)
    app = PAPlotWidget()
    app.show()
    sys.exit(q_app.exec_())
