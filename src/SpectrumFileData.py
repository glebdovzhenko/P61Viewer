import os
import json
import h5py
import pandas as pd
import numpy as np
from matplotlib.lines import Line2D


class SpectrumFileData:
    def __init__(self, name):
        self._name = name
        self._show = True
        self.plot_color = None
        self.spectrum_data = None
        self.spectrum_metadata = None
        self.plot_line = None

    def short_name(self):
        tmp = os.path.basename(self._name)
        if len(tmp) > 30:
            return '...' + tmp[-30:]
        else:
            return '.../' + tmp

    def show(self):
        return self._show

    def change_show_status(self):
        self._show = not self._show

    def set_show_status(self, value):
        self._show = value

    def set_name(self, new_name):
        self._name = new_name

    def set_plot_color(self, color):
        self.plot_color = color
        self.plot_line.set_color(color)

    def get_color(self):
        return int(self.plot_color[1:3], 16), int(self.plot_color[3:5], 16), int(self.plot_color[5:7], 16)

    def get_name(self):
        return self._name

    def __repr__(self):
        return ('x' if self.show() else 'o') + ' ' + self.short_name()

    def init_from_h5(self, f_name):
        # TODO: is this good?
        try:
            with h5py.File(f_name, 'r') as f:
                self.spectrum_data = pd.DataFrame(f['Spectrum'][:], columns=['keV', 'Int'])
                self.spectrum_metadata = json.loads(f['Metadata'][()])
                self.set_name(f_name)
                self.plot_line = Line2D(self.spectrum_data['keV'], self.spectrum_data['Int'])
                return True
        except Exception as e:
            return False

    def init_from_nexus(self, f_name, channel):
        try:
            with h5py.File(f_name, 'r') as f:
                frames = np.sum(f['entry/instrument/xspress3/%s/histogram' % channel][:], axis=0)
                bins = np.arange(frames.shape[0])
                print(frames)
                print(bins)
                self.spectrum_data = pd.DataFrame({'Bins': bins, 'Int': frames})
                self.set_name(f_name + ':' + channel)
                self.plot_line = Line2D(self.spectrum_data['Bins'], self.spectrum_data['Int'])
                return True
        except Exception as e:
            print(e)
            return False