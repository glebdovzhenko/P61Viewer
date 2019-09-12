import h5py
import os
from matplotlib import pyplot as plt
import numpy as np


def visitor_func(name, node):
    if isinstance(node, h5py.Dataset):
        if len(node.shape) == 1:
            v = node[:]
            print(name, ' ' * (55 - len(name)), v)
        else:
            print(name, ' ' * (55 - len(name)), node)


if __name__ == '__main__':
    wd = '/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/test_tango'
    for f_name in os.listdir(wd):
        print('#' * 20, f_name, '#' * 20)
        with h5py.File(os.path.join(wd, f_name), 'r') as f:
            f.visititems(visitor_func)
            ch0, ch1 = f['entry/instrument/xspress3/channel00/histogram'], \
                       f['entry/instrument/xspress3/channel01/histogram']

            fig = plt.figure(f_name)
            ax0 = fig.add_subplot(121)
            ax0.title.set_text('Channel 0')
            ax1 = fig.add_subplot(122)
            ax1.title.set_text('Channel 1')
            ch0 = np.sum(ch0, axis=0)
            ch1 = np.sum(ch1, axis=0)
            ax0.plot(ch0)
            ax1.plot(ch1)
        print('\n' * 3)
    plt.show()

