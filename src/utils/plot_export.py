import pandas as pd
from matplotlib import pyplot as plt


if __name__ == '__main__':
    d = pd.read_csv('../../test_files/exports/s45_ep_peo_00023.csv', header=0, index_col=0)

    plt.figure()
    for col in d.columns:
        if 'amplitude' not in col or 'std' in col:
            continue
        plt.plot(d[col],
                 label='%01f' % d[col.replace('amplitude', 'center')].mean())
    plt.legend(bbox_to_anchor=(1.05, 1))
    plt.xlabel('Spectrum #')
    plt.ylabel('Peak amplitude (normalised)')
    plt.show()