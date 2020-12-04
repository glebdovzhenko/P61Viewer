from lmfit import model, models
import copy
import scipy
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

    def make_params(self, verbose=False, **kwargs):
        pars = super().make_params(verbose, **kwargs)
        pars.add(name=self.prefix + 'peak_base',
                 value=3.,
                 min=0., max=7.,
                 vary=False)
        return pars


class InterpolationModel(model.Model):
    def __init__(self, **kwargs):
        def LinearInterpolation(x, interp_fn=0., peak_base=3.):
            return np.zeros(shape=x.shape)

        model.Model.__init__(self, LinearInterpolation, **kwargs)
        self.refine = True

    def make_params(self, verbose=False, **kwargs):
        pars = model.Model.make_params(self, verbose, **kwargs)
        pars[self.prefix + 'peak_base'].vary = False
        pars[self.prefix + 'peak_base'].min = 0.
        pars[self.prefix + 'peak_base'].max = 7.
        return pars


models.PolynomialModel = PolynomialModel
models.InterpolationModel = InterpolationModel
fit_kwargs = {'method': 'least_squares'}
peak_md_names = ('GaussianModel', 'LorentzianModel', 'PseudoVoigtModel', 'Pearson7Model',
                 'SkewedGaussianModel', 'SkewedVoigtModel', 'SplitLorentzianModel')
background_md_names = ('PolynomialModel', 'InterpolationModel')
prefixes = {'GaussianModel': 'g', 'LorentzianModel': 'lor', 'Pearson7Model': 'pvii', 'PolynomialModel': 'pol',
                'PseudoVoigtModel': 'pv', 'SkewedGaussianModel': 'sg', 'SkewedVoigtModel': 'sv',
                'SplitLorentzianModel': 'spl', 'InterpolationModel': 'int'}


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
    param_stderr = dict()
    for model in result.model.components:
        if is_bckg_md(model) != reverse:
            for param in result.params:
                if model.prefix in param:
                    param_status[param] = result.params[param].vary
                    param_stderr[param] = result.params[param].stderr
                    result.params[param].vary = False
    return result, param_status, param_stderr


def fix_outlier_peaks(result, x_lim):
    """
    Fixes all parameters for peaks whose centers are outside of the region x_lim
    :param result:
    :return:
    """
    param_status = dict()
    param_stderr = dict()
    for model in result.model.components:
        if is_peak_md(model):
            if not x_lim[0] <= result.params[model.prefix + 'center'].value <= x_lim[1]:
                for param in result.params:
                    if model.prefix in param:
                        param_status[param] = result.params[param].vary
                        param_stderr[param] = result.params[param].stderr
                        result.params[param].vary = False
    return result, param_status, param_stderr


def sort_components(md: model.ModelResult) -> Iterable:
    def key(cmp):
        if is_peak_md(cmp):
            return md.params[cmp.prefix + 'center'].value
        else:
            return -1
    return sorted(md.model.components, key=key)


def constrain_params(md: model.ModelResult,
                     center_vary: float,
                     height_min: float, height_max: float,
                     sigma_min: float, sigma_max: float) -> model.ModelResult:

    for param in md.params:
        if 'height' in param:
            md.params[param].min = max(0.0, height_min)
            md.params[param].max = height_max
        if 'center' in param:
            vary = md.params[param.replace('center', 'sigma')].value * center_vary
            md.params[param].min = md.params[param].value - vary
            md.params[param].max = md.params[param].value + vary
        if 'sigma' in param:
            md.params[param].min = md.params[param].value * sigma_min
            md.params[param].max = md.params[param].value * sigma_max
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
        if smd['name'] == 'PolynomialModel':
            init_params = {'degree': len(smd['params']) - 1}
        else:
            init_params = dict()
        result = add_md(smd['name'], init_params, result, prefix=smd['prefix'])

        for param in smd['params']:
            for key in ('name', 'value', 'min', 'max', 'vary'):
                setattr(result.params[param['name']], key, param[key])

    return result


def get_peak_intervals(mr: model.ModelResult, overlap_base=None, interval_base=None) -> Iterable:
    def recursive_merge(inter, start_index=0):
        for i in range(start_index, len(inter) - 1):
            if inter[i][1] > inter[i + 1][0]:
                new_start = inter[i][0]
                new_end = inter[i + 1][1]
                inter[i] = [new_start, new_end]
                del inter[i + 1]
                return recursive_merge(inter.copy(), start_index=i)
        return inter

    if overlap_base is None:
        for par in mr.params:
            if 'peak_base' in mr.params[par].name:
                overlap_base = mr.params[par].value
                break
        else:
            overlap_base = 3.

    if interval_base is None:
        interval_base = overlap_base

    if interval_base < overlap_base:
        raise ValueError('Overlap base of a peak should be less than its whole base')

    overlap_intervals = []
    for cmp in mr.model.components:
        if is_peak_md(cmp):
            overlap_intervals.append([mr.params[cmp.prefix + 'center'].value -
                                      overlap_base * mr.params[cmp.prefix + 'sigma'].value,
                                      mr.params[cmp.prefix + 'center'].value +
                                      overlap_base * mr.params[cmp.prefix + 'sigma'].value
                                     ])

    overlap_intervals = recursive_merge(overlap_intervals)
    result = []
    for l, r in overlap_intervals:
        tmp = []
        for cmp in mr.model.components:
            if is_peak_md(cmp):
                if l < mr.params[cmp.prefix + 'center'].value < r:
                    tmp.append([
                        mr.params[cmp.prefix + 'center'].value -
                        interval_base * mr.params[cmp.prefix + 'sigma'].value,
                        mr.params[cmp.prefix + 'center'].value +
                        interval_base * mr.params[cmp.prefix + 'sigma'].value
                    ])
        tmp = recursive_merge(tmp)

        result.extend(tmp)

    print(result)
    return result


def refine_interpolation_md(mr: model.ModelResult, **kwargs) -> model.ModelResult:
    interp, base, refine = None, None, False
    for cmp in mr.model.components:
        if cmp._name == 'InterpolationModel':
            interp = cmp
            base = mr.params[cmp.prefix + 'peak_base'].value
            refine = mr.params[cmp.prefix + 'interp_fn'].vary

    if refine:
        i_xx, i_yy = kwargs['x'], kwargs['data']
        for cmp in mr.model.components:
            if is_peak_md(cmp):
                base_min = mr.params[cmp.prefix + 'center'].value - base * mr.params[cmp.prefix + 'sigma'].value
                base_max = mr.params[cmp.prefix + 'center'].value + base * mr.params[cmp.prefix + 'sigma'].value
                i_yy = i_yy[(i_xx <= base_min) | (i_xx >= base_max)]
                i_xx = i_xx[(i_xx <= base_min) | (i_xx >= base_max)]
        func = scipy.interpolate.interp1d(i_xx, i_yy, kind='linear')
        interp.func = lambda x, interp_fn, peak_base: func(x)

    return mr


def fit(mr: model.ModelResult, **kwargs) -> model.ModelResult:
    mr = refine_interpolation_md(mr, **kwargs)
    mr.fit(**kwargs)
    return mr


def update_varied_params(mr1: model.ModelResult, mr2: model.ModelResult) -> model.ModelResult:
    for par in mr2.params:
        if mr2.params[par].vary and (par in mr1.params):
            mr1.params[par] = copy.copy(mr2.params[par])
    return mr1
