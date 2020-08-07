from lmfit import model, models
import numpy as np
from functools import reduce


def make_prefix(name, composite):
    """
    Generates a unique prefix for the new model.

    :param name:
    :param composite:
    :return:
    """
    prefixes = {'GaussianModel': 'g', 'LorentzianModel': 'lor', 'Pearson7Model': 'pvii', 'PolynomialModel': 'pol',
                'PseudoVoigtModel': 'pv', 'SkewedGaussianModel': 'sg', 'SkewedVoigtModel': 'sv',
                'SplitLorentzianModel': 'spl'}

    if composite is None:
        return prefixes[name] + '0_'

    used_prefixes = [md.prefix for md in composite.model.components]
    for ii in range(100):
        if prefixes[name] + '%d_' % ii not in used_prefixes:
            return prefixes[name] + '%d_' % ii


def rm_md(prefix, composite):
    """
    Removes the model identified by prefix from the composite model

    :param prefix:
    :param composite:
    :return:
    """
    if len(composite.model.components) == 1:
        return None

    new_md = reduce(lambda a, b: a + b, (cmp for cmp in composite.model.components if cmp.prefix != prefix))
    new_params = composite.params.copy()
    for par in composite.params:
        if prefix in composite.params[par].name:
            new_params.pop(par)

    composite.model = new_md
    composite.params = new_params

    return composite


def add_md(name, init_params, composite):
    """
    Adds the model intialised with init_params to the composite model.

    :param name:
    :param init_params:
    :param composite:
    :return:
    """
    kwargs = {'name': name}

    if name == 'PolynomialModel':
        if 'degree' in init_params:
            kwargs['degree'] = init_params.pop('degree')
        else:
            kwargs['degree'] = 3

    kwargs['prefix'] = make_prefix(name, composite)
    new_md = getattr(models, name)(**kwargs)

    if composite is None:
        return model.ModelResult(new_md, new_md.make_params(**init_params))
    elif isinstance(composite, model.ModelResult):
        params = composite.params
        params.update(new_md.make_params(**init_params))
        return model.ModelResult(composite.model + new_md, params)


def add_peak_md(name, peak_list, composite):
    if name not in ('GaussianModel', 'LorentzianModel', 'PseudoVoigtModel'):
        return composite

    for ta in peak_list:
        for peak in ta['peaks']:
            width = peak['right_ip'] - peak['left_ip']
            sigma = width / (2. * np.sqrt(2. * np.log(2)))

            prefix = make_prefix(name, composite)
            kwargs = {'name': name, 'prefix': prefix}
            new_md = getattr(models, name)(**kwargs)
            params = new_md.make_params()

            params[prefix + 'amplitude'].min = 0.

            params[prefix + 'center'].value = peak['center_x']
            params[prefix + 'center'].min = peak['center_x'] - .25 * width
            params[prefix + 'center'].max = peak['center_x'] + .25 * width

            params[prefix + 'sigma'].max = 10.
            params[prefix + 'sigma'].min = 0.1

            params[prefix + 'height'].max = 1.5 * peak['center_y']

            if name == 'GaussianModel':
                params[prefix + 'amplitude'].value = peak['center_y'] * np.sqrt(2. * np.pi) * sigma
                params[prefix + 'sigma'].value = sigma
            elif name == 'LorentzianModel':
                params[prefix + 'amplitude'].value = peak['center_y'] * np.pi * 0.5 * width
                params[prefix + 'sigma'].value = 0.5 * width
            elif name == 'PseudoVoigtModel':
                params[prefix + 'amplitude'].value = peak['center_y'] * np.sqrt(2. * np.pi) * sigma / np.sqrt(2. * np.log(2))
                params[prefix + 'sigma'].value = sigma
                params[prefix + 'fraction'].value = 0.

            c_params = composite.params
            c_params.update(params)
            composite = model.ModelResult(composite.model + new_md, c_params)

    return composite
