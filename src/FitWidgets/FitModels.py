import numpy as np
from lmfit.models import LinearModel, GaussianModel, LorentzianModel, PseudoVoigtModel, VoigtModel


if __name__ == '__main__':
    gm, lm, pvm = GaussianModel() + LinearModel(), LorentzianModel() + LinearModel(), PseudoVoigtModel() + LinearModel()

    from NexusHistogram import NexusHistogram
    from matplotlib import pyplot as plt

    md = PseudoVoigtModel()

    print(md.param_names)

    # data = NexusHistogram()
    # data.fill('/Users/glebdovzhenko/Dropbox/PycharmProjects/P61BViewer/test_files/collected/Co57_2019-09-30_09-10-30_.nxs',
    #           'entry/instrument/xspress3/channel00/histogram', 'ch0')
    # dataset = data.dataset[120:124]
    # xx, yy = np.array(dataset.index), np.array(dataset.values)
    #
    # pars = PseudoVoigtModel().guess(yy, x=xx)
    # pars.update(LinearModel().guess(yy, x=xx))
    #
    # out = pvm.fit(yy, pars, x=xx)
    # print(out.fit_report())
    # print(pvm.params['amplitude'].value)
    #
    # plt.plot(xx, yy, 'o')
    # plt.plot(xx, out.best_fit)
    # plt.show()