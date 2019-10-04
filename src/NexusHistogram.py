import numpy as np
import h5py
from matplotlib.lines import Line2D


class NexusHistogram:
    kev_per_bin = 5E-2

    def __init__(self):
        self._dataset = None         # internal
        self._intensities = None     # internal
        self._energies = None        # internal
        self._name = ''              # only get
        self._dataset_id = ''        # internal
        self._active = True          # get & set
        self._plot_color_mpl = None  # only get
        self._plot_color_qt = None   # only get
        self._plot_line = None       # only get

    def get_name(self):
        return self._name

    def set_name(self, nval):
        if not isinstance(nval, str):
            raise ValueError(nval, 'of type', type(nval),  ' was passed as NexusFile.name and it should be str.')
        self._name = nval

    def get_active(self):
        return self._active

    def set_active(self, nval):
        if not isinstance(nval, bool):
            raise ValueError(nval, 'of type', type(nval),  ' was passed as NexusFile.active and it should be bool.')
        self._active = nval

    def get_plot_line(self):
        return self._plot_line

    def get_plot_color_qt(self):
        return self._plot_color_qt

    def get_plot_color_mpl(self):
        return self._plot_color_mpl

    def set_plot_color_mpl(self, nval):
        if not isinstance(nval, str):
            raise ValueError(nval, 'of type', type(nval), ' was passed as NexusFile.plot_color and it should be str.')
        self._plot_color_mpl = nval
        self._plot_color_qt = int(self._plot_color_mpl[1:3], 16), int(self._plot_color_mpl[3:5], 16), \
                              int(self._plot_color_mpl[5:7], 16)
        self._plot_line.set_color(nval)

    def get_dataset_id(self):
        return self._dataset_id

    name = property(fget=get_name, fset=set_name)
    active = property(fget=get_active, fset=set_active)
    plot_line = property(fget=get_plot_line)
    plot_color_mpl = property(fget=get_plot_color_mpl, fset=set_plot_color_mpl)
    plot_color_qt = property(fget=get_plot_color_qt)
    dataset_id = property(fget=get_dataset_id)

    def fill(self, file, field, name):
        try:
            self._name = name
            self._dataset_id = file + ':' + field

            with h5py.File(file, 'r') as f:
                frames = np.sum(f[field], axis=0)
                frames[:20] = 0.0
                frames[-1] = 0.0
                kev = (np.arange(frames.shape[0]) + 0.5) * self.kev_per_bin

                self._intensities = frames
                self._energies = kev
                self._plot_line = Line2D(self._energies, self._intensities)

                # TODO: add metadata fill

        except Exception as e:
            print(e)
            return False

        return True
