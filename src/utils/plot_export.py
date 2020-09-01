import pandas as pd
from matplotlib import pyplot as plt


if __name__ == '__main__':
    # '../../test_files/exports/Probe_TBB_2379_sin2psi_06082015.csv'
    d = pd.read_csv('/Users/glebdovzhenko/Dropbox/P61 Viewer/Probe_5-5_sin2psi_04082015.csv', header=0, index_col=0)
    plt.figure()
    for col in d.columns:
        if 'height' not in col or 'std' in col:
            continue
        plt.plot(d[col],
                 label='%01f' % d[col.replace('height', 'center')].mean())
        # plt.plot(d[col.replace('height', 'center')],
        #                    label='%01f' % d[col.replace('height', 'center')].mean())
    plt.legend(bbox_to_anchor=(1.05, 1))
    plt.xlabel('Spectrum #')
    plt.ylabel('Peak amplitude (normalised)')
    plt.show()
    