import os
import json
import h5py
import pandas as pd


class SpectrumFileData:
    def __init__(self, name):
        self._name = name
        self._show = True
        self.plot_color = None
        self.spectrum_data = None
        self.spectrum_metadata = None

    def short_name(self):
        tmp = os.path.basename(self._name)
        if len(tmp) > 20:
            return '...' + tmp[-20:]
        else:
            return '.../' + tmp

    def show(self):
        return self._show

    def change_show_status(self):
        self._show = not self._show

    def set_name(self, new_name):
        self._name = new_name

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
                return True
        except Exception as e:
            return False
