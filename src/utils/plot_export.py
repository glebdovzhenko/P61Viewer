import pandas as pd
from matplotlib import pyplot as plt


if __name__ == '__main__':
    # '../../test_files/exports/Probe_TBB_2379_sin2psi_06082015.csv'
    d = pd.read_csv('/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/test_files/exports/sequential.csv',
                    header=0, index_col=0)
    fig = plt.figure()
    for col in d.columns:
        if 'height' not in col or 'std' in col:
            continue
        plt.subplot(211)
        plt.errorbar(x=d[col].index, y=d[col], yerr=d[col + '_std'], label=None)
        plt.subplot(212)
        plt.errorbar(x=d[col.replace('height', 'center')].index,
                     y=d[col.replace('height', 'center')],
                     yerr=d[col.replace('height', 'center') + '_std'],
                     label='%01f' % d[col.replace('height', 'center')].mean())
    fig.legend(bbox_to_anchor=(1.15, 0.85))
    plt.subplot(211)
    plt.ylabel('Peak amplitude')
    plt.subplot(212)
    plt.ylabel('Peak center')
    plt.xlabel('Spectrum #')
    plt.show()
