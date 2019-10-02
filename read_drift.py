import pandas as pd
from matplotlib import pyplot as plt
import os


if __name__ == '__main__':
    names = {0: 'Background', 3: 'W', 8: 'Mb'}
    for ii, ff in enumerate(sorted(filter(lambda x: '20191002' in x, os.listdir('test_files/drift')))):
        dd = pd.read_csv(os.path.join('test_files/drift', ff), skiprows=6, header=None)

        if ii in (0, 3, 8):
            plt.figure(names[ii])

        plt.plot(dd[0], dd[1], label=ff)
        print(dd[1].sum() / 50.)

        if ii in (2, 7, 17):
            plt.legend()
            plt.xlabel('Energy, [eV]')
            plt.ylabel('Intensity, [counts]')

    plt.show()
