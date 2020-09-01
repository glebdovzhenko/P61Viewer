from lmfit import model, models, lineshapes
import numpy as np
from functools import reduce
from typing import Iterable, Union


class PolynomialModel(models.PolynomialModel):
    def __init__(self, degree, independent_vars=['x'], prefix='',
                 nan_policy='raise', **kwargs):
        kwargs.update({'prefix': prefix, 'nan_policy': nan_policy,
                       'independent_vars': independent_vars})
        if not isinstance(degree, int) or degree > self.MAX_DEGREE:
            raise TypeError(self.DEGREE_ERR % self.MAX_DEGREE)

        self.poly_degree = degree
        pnames = ['c%i' % (i) for i in range(degree + 1)]
        kwargs['param_names'] = pnames

        def polynomial(x, c0=0, c1=0, c2=0, c3=0, c4=0, c5=0, c6=0, c7=0):
            return np.abs(np.polyval([c7, c6, c5, c4, c3, c2, c1, c0], x))

        model.Model.__init__(self, polynomial, **kwargs)


models.PolynomialModel = PolynomialModel
fit_kwargs = {'method': 'least_squares'}
peak_md_names = ('GaussianModel', 'LorentzianModel', 'PseudoVoigtModel', 'Pearson7Model',
                 'SkewedGaussianModel', 'SkewedVoigtModel', 'SplitLorentzianModel')
background_md_names = ('PolynomialModel', )


def is_peak_md(md: Union[str, model.Model]) -> bool:
    if isinstance(md, str):
        return md in peak_md_names
    elif isinstance(md, model.Model):
        for name in peak_md_names:
            if name in md.name:
                return True
        else:
            return False
    return False


def is_bckg_md(md: Union[str, model.Model]) -> bool:
    if isinstance(md, str):
        return md in background_md_names
    elif isinstance(md, model.Model):
        for name in background_md_names:
            if name in md.name:
                return True
        else:
            return False
    return False


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


def add_md(name, init_params, composite, prefix=None):
    """
    Adds the model intialised with init_params to the composite model.

    :param name:
    :param init_params:
    :param composite:
    :param prefix:
    :return:
    """
    kwargs = {'name': name}

    if name == 'PolynomialModel':
        if 'degree' in init_params:
            kwargs['degree'] = init_params.pop('degree')
        else:
            kwargs['degree'] = 3

    if prefix is None:
        kwargs['prefix'] = make_prefix(name, composite)
    else:
        kwargs['prefix'] = prefix

    new_md = getattr(models, name)(**kwargs)

    if composite is None:
        return model.ModelResult(new_md, new_md.make_params(**init_params))
    elif isinstance(composite, model.ModelResult):
        params = composite.params
        params.update(new_md.make_params(**init_params))
        return model.ModelResult(composite.model + new_md, params)


def add_peak_md(name, peak_list, composite):
    if not is_peak_md(name):
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
            params[prefix + 'sigma'].min = 0.01

            params[prefix + 'height'].max = 1.5 * peak['center_y']

            if 'Cut' in name:
                params[prefix + 'cutoff'].vary = False
                params[prefix + 'cutoff'].min = 1.
                params[prefix + 'cutoff'].max = 3.

            if name == 'GaussianModel':
                params[prefix + 'amplitude'].value = peak['center_y'] * np.sqrt(2. * np.pi) * sigma
                params[prefix + 'sigma'].value = sigma
            elif name == 'LorentzianModel':
                params[prefix + 'amplitude'].value = peak['center_y'] * np.pi * 0.5 * width
                params[prefix + 'sigma'].value = 0.5 * width
            elif name == 'PseudoVoigtModel':
                params[prefix + 'amplitude'].value = peak['center_y'] * np.sqrt(2. * np.pi) * sigma / np.sqrt(
                    2. * np.log(2))
                params[prefix + 'sigma'].value = sigma
                params[prefix + 'fraction'].value = 0.

            if composite is not None:
                c_params = composite.params
                c_params.update(params)
                composite = model.ModelResult(composite.model + new_md, c_params)
            else:
                composite = model.ModelResult(new_md, params)

    return composite


def fix_background(result, reverse=False):
    """
    Fixes background parameters (sets them not to vary). If reverse == False, fixes everything except the background
    :param result:
    :param reverse:
    :return:
    """
    param_status = dict()
    for model in result.model.components:
        if is_bckg_md(model) != reverse:
            for param in result.params:
                if model.prefix in param:
                    param_status[param] = result.params[param].vary
                    result.params[param].vary = False
    return result, param_status


def fix_outlier_peaks(result, x_lim):
    """
    Fixes all parameters for peaks whose centers are outside of the region x_lim
    :param result:
    :return:
    """
    param_status = dict()
    for model in result.model.components:
        if is_peak_md(model):
            if not x_lim[0] <= result.params[model.prefix + 'center'].value <= x_lim[1]:
                for param in result.params:
                    if model.prefix in param:
                        param_status[param] = result.params[param].vary
                        result.params[param].vary = False
    return result, param_status


def sort_components(md: model.ModelResult) -> Iterable:
    def key(cmp):
        if is_peak_md(cmp):
            return md.params[cmp.prefix + 'center'].value
        else:
            return -1
    return sorted(md.model.components, key=key)


def constrain_params(md: model.ModelResult) -> model.ModelResult:
    sigmas = []
    for param in md.params:
        if 'sigma' in param:
            sigmas.append(md.params[param].value)

    for param in md.params:
        if 'amplitude' in param:
            md.params[param].min = 0.0
        if 'center' in param:
            quarter_width = .5 * np.sqrt(2. * np.log(2)) * md.params[param.replace('center', 'sigma')].value
            md.params[param].min = md.params[param].value - quarter_width
            md.params[param].max = md.params[param].value + quarter_width
        if 'sigma' in param:
            md.params[param].min = 0.
            md.params[param].max = 1.1 * np.max(sigmas)
    return md


def serialize_model_result(md: model.ModelResult) -> list:
    result = []
    for cmp in md.model.components:
        serialized = dict()
        serialized['name'] = cmp._name
        serialized['prefix'] = cmp.prefix
        serialized['params'] = []
        for param in md.params:
            if cmp.prefix in md.params[param].name:
                serialized['params'].append(
                    {key: getattr(md.params[param], key) for key in ('name', 'value', 'min', 'max', 'vary')}
                )

        result.append(serialized)

    return result


def deserialize_model_result(struct: list) -> model.ModelResult:
    result = None
    for smd in struct:
        print(smd)
        if smd['name'] == 'PolynomialModel':
            init_params = {'degree': len(smd['params']) - 1}
        else:
            init_params = dict()
        result = add_md(smd['name'], init_params, result, prefix=smd['prefix'])

        for param in smd['params']:
            for key in ('name', 'value', 'min', 'max', 'vary'):
                setattr(result.params[param['name']], key, param[key])

    return result
