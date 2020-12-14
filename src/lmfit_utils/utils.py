from lmfit import model, models
import copy
import scipy
import numpy as np
from functools import reduce
from typing import Iterable, Union
import logging

logger = logging.getLogger('lmfit_utils')


class InterpolationModel(model.Model):
    # TODO: make fit not crash if the xmin-xmax range is extended
    def __init__(self, **kwargs):
        def LinearInterpolation(x, interp_fn=0., xmin=0., xmax=200.):
            return np.zeros(shape=x.shape)

        model.Model.__init__(self, LinearInterpolation, **kwargs)
        self.refine = True


class PolynomialModel(model.Model):
    def __init__(self, degree, independent_vars=['x'], prefix='',
                 nan_policy='raise', **kwargs):
        kwargs.update({'prefix': prefix, 'nan_policy': nan_policy,
                       'independent_vars': independent_vars})

        self.poly_degree = degree
        pnames = ['c%i' % i for i in range(degree + 1)]
        kwargs['param_names'] = pnames + ['xmin', 'xmax']

        def polynomial(x, xmin=0, xmax=200, c0=0, c1=0, c2=0, c3=0, c4=0, c5=0, c6=0, c7=0):
            y = np.zeros(x.shape)
            y[(x > xmin) & (x < xmax)] = np.polyval([c7, c6, c5, c4, c3, c2, c1, c0], x[(x > xmin) & (x < xmax)])
            return np.abs(y)

        super().__init__(polynomial, **kwargs)

    def make_params(self, verbose=False, **kwargs):
        params = super().make_params()
        for par in params:
            params[par].value = 0.
        params[self.prefix + 'xmin'].vary = False
        params[self.prefix + 'xmax'].vary = False
        params[self.prefix + 'xmax'].value = 200.
        return params


def upd_peak_mds(md):
    def make_params(self, verbose=False, **kwargs):
        pars = super(md, self).make_params(verbose, **kwargs)
        pars[self.prefix + 'amplitude'].min = 0.

        pars.add(name=self.prefix + 'base',
                 value=3.,
                 min=0., max=7.,
                 vary=False)
        pars.add(name=self.prefix + 'overlap_base',
                 value=3.,
                 min=0., max=7.,
                 vary=False)
        return pars

    md.make_params = make_params


upd_peak_mds(models.GaussianModel)
upd_peak_mds(models.LorentzianModel)
upd_peak_mds(models.PseudoVoigtModel)
upd_peak_mds(models.Pearson7Model)
upd_peak_mds(models.SkewedGaussianModel)
upd_peak_mds(models.SkewedVoigtModel)
upd_peak_mds(models.SplitLorentzianModel)
models.InterpolationModel = InterpolationModel
models.PolynomialModel = PolynomialModel


fit_kwargs = {'method': 'least_squares'}
peak_md_names = ('GaussianModel',
                 'LorentzianModel',
                 'PseudoVoigtModel',
                 'Pearson7Model',
                 'SkewedGaussianModel',
                 'SkewedVoigtModel',
                 'SplitLorentzianModel')
background_md_names = ('PolynomialModel',
                       'InterpolationModel')
prefixes = {'GaussianModel': 'gau',
            'LorentzianModel': 'lor',
            'Pearson7Model': 'pvii',
            'PolynomialModel': 'pol',
            'PseudoVoigtModel': 'pv',
            'SkewedGaussianModel': 'sg',
            'SkewedVoigtModel': 'sv',
            'SplitLorentzianModel': 'spl',
            'InterpolationModel': 'int'}


def is_param_editable(p: model.Parameter) -> bool:
    """
    Returns True if the user should be allowed to edit this parameter in GUI.
    """
    if p.expr is not None:
        return False
    elif ('fwhm' in p.name) or ('height' in p.name) or ('interp_fn' in p.name):
        return False
    else:
        return True


def is_param_refinable(p: model.Parameter) -> bool:
    """
    Returns True if the user should be allowed to refine this parameter in GUI.
    """
    if p.expr is not None:
        return False
    elif ('fwhm' in p.name) or ('height' in p.name) or ('base' in p.name) or \
            ('xmin' in p.name) or ('xmax' in p.name):
        return False
    else:
        return True


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


def make_prefix(name: str, mr: model.ModelResult) -> str:
    """
    Generates a unique prefix for a new model to be added to the ModelResult as a component.

    :param name:
    :param mr:
    :return:
    """

    if mr is None:
        return prefixes[name] + '0_'

    used_prefixes = [md.prefix for md in mr.model.components]
    for ii in range(100):
        if prefixes[name] + '%d_' % ii not in used_prefixes:
            return prefixes[name] + '%d_' % ii


def rm_md(prefix: str, mr: model.ModelResult) -> Union[model.ModelResult, None]:
    """
    Removes the model identified by prefix from the ModelResult

    :param prefix:
    :param mr:
    :return:
    """
    if len(mr.model.components) == 1:
        return None

    new_md = reduce(lambda a, b: a + b, (cmp for cmp in mr.model.components if cmp.prefix != prefix))
    new_params = mr.params.copy()
    for par in mr.params:
        if prefix in mr.params[par].name:
            new_params.pop(par)

    mr.model = new_md
    mr.params = new_params

    return mr


def add_md(name: str, init_params: dict, composite: Union[None, model.ModelResult],
           prefix: Union[None, str] = None) -> model.ModelResult:
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

            params[prefix + 'sigma'].max = 1.1 * params[prefix + 'sigma'].value
            params[prefix + 'sigma'].min = 0.9 * params[prefix + 'sigma'].value

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


def get_peak_intervals(mr: model.ModelResult) -> Iterable:
    def recursive_merge(inter, start_index=0):
        for i in range(start_index, len(inter) - 1):
            if (min(inter[i + 1]) <= inter[i][0] <= max(inter[i + 1])) or \
                    (min(inter[i + 1]) <= inter[i][1] <= max(inter[i + 1])):
                inter[i] = [min(inter[i][0], inter[i + 1][0]), max(inter[i][1], inter[i + 1][1])]
                del inter[i + 1]
                return recursive_merge(inter.copy(), start_index=i)
        return inter

    overlap_intervals = []
    for cmp in mr.model.components:
        if is_peak_md(cmp):
            overlap_intervals.append([mr.params[cmp.prefix + 'center'].value -
                                      mr.params[cmp.prefix + 'overlap_base'].value *
                                      mr.params[cmp.prefix + 'sigma'].value,

                                      mr.params[cmp.prefix + 'center'].value +
                                      mr.params[cmp.prefix + 'overlap_base'].value *
                                      mr.params[cmp.prefix + 'sigma'].value
                                      ])
    overlap_intervals = recursive_merge(overlap_intervals, 0)

    result = []
    for l, r in overlap_intervals:
        tmp = []
        for cmp in mr.model.components:
            if is_peak_md(cmp):
                if l < mr.params[cmp.prefix + 'center'].value < r:
                    tmp.append([
                        mr.params[cmp.prefix + 'center'].value -
                        mr.params[cmp.prefix + 'base'].value * mr.params[cmp.prefix + 'sigma'].value,
                        mr.params[cmp.prefix + 'center'].value +
                        mr.params[cmp.prefix + 'base'].value * mr.params[cmp.prefix + 'sigma'].value
                    ])
        result.extend(recursive_merge(tmp, 0))

    return list(sorted(result, key=lambda x: x[0]))


def refine_interpolation_md(mr: model.ModelResult, **kwargs) -> model.ModelResult:
    interp, refine, xmin, xmax = None, False, None, None
    for cmp in mr.model.components:
        if cmp._name == 'InterpolationModel':
            interp = cmp
            refine = mr.params[cmp.prefix + 'interp_fn'].vary
            xmin = mr.params[cmp.prefix + 'xmin'].value
            xmax = mr.params[cmp.prefix + 'xmax'].value

    if refine:
        i_xx, i_yy = kwargs['x'], kwargs['data']
        for cmp in mr.model.components:
            if is_peak_md(cmp):
                base_min = mr.params[cmp.prefix + 'center'].value - \
                           mr.params[cmp.prefix + 'base'].value * mr.params[cmp.prefix + 'sigma'].value
                base_max = mr.params[cmp.prefix + 'center'].value + \
                           mr.params[cmp.prefix + 'base'].value * mr.params[cmp.prefix + 'sigma'].value
                i_yy = i_yy[(i_xx <= base_min) | (i_xx >= base_max)]
                i_xx = i_xx[(i_xx <= base_min) | (i_xx >= base_max)]

                if base_min <= xmin <= base_max:
                    xmin = i_xx[i_xx <= base_min]
                    if xmin.shape[0] == 0:
                        xmin = base_min
                    else:
                        xmin = np.max(xmin)

                if base_min <= xmax <= base_max:
                    xmax = i_xx[i_xx >= base_max]
                    if xmax.shape[0] == 0:
                        xmax = base_max
                    else:
                        xmax = np.min(xmax)

        i_yy = i_yy[(i_xx >= xmin) & (i_xx <= xmax)]
        i_xx = i_xx[(i_xx >= xmin) & (i_xx <= xmax)]
        func = scipy.interpolate.interp1d(i_xx, i_yy, kind='linear')

        def new_fn(x, interp_fn, xmin, xmax):
            res = np.zeros(x.shape)
            res[(x > xmin) & (x < xmax)] = func(x[(x > xmin) & (x < xmax)])
            return res

        interp.func = new_fn

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


def update_varied_constraints(mr: model.ModelResult, d_center=0.25, d_sigma=0.1) -> model.ModelResult:
    for par in mr.params:
        if not mr.params[par].vary:
            continue
        if 'center' in par:
            mr.params[par].min = mr.params[par].value - d_center * mr.params[par.replace('center', 'sigma')].value
            mr.params[par].max = mr.params[par].value + d_center * mr.params[par.replace('center', 'sigma')].value
        if 'sigma' in par:
            mr.params[par].min = (1. - d_sigma) * mr.params[par].value
            mr.params[par].max = (1. + d_sigma) * mr.params[par].value
    return mr


def fit_peaks(xx, yy, result):
    result, vary_bckg, bckg_stderr = fix_background(result)

    if any((result.params[p].vary for p in result.params)):
        for l, r in get_peak_intervals(result):
            logger.info('fit_peaks: refining interval [%.01f, %.01f]' % (l, r))
            xx_, yy_ = xx.copy(), yy.copy()
            yy_ = yy_[(xx_ > l) & (xx_ < r)]
            xx_ = xx_[(xx_ > l) & (xx_ < r)]
            if xx_.shape[0] == 0:
                continue

            result, vary_peaks, peaks_stderr = fix_outlier_peaks(result, (np.min(xx_), np.max(xx_)))
            result = update_varied_params(result, fit(result, data=yy_, x=xx_, **fit_kwargs))
            result = update_varied_constraints(result)

            for param in vary_peaks:
                result.params[param].vary = vary_peaks[param]
                result.params[param].stderr = peaks_stderr[param]

    for param in vary_bckg:
        result.params[param].vary = vary_bckg[param]
        result.params[param].stderr = bckg_stderr[param]

    return result


def fit_bckg(xx, yy, result):
    result, vary_bckg, bckg_stderr = fix_background(result, reverse=True)

    if any((result.params[p].vary for p in result.params)):
        minx, maxx, miny, maxy = xx[0], xx[-1], yy[0], yy[-1]
        for l, r in get_peak_intervals(result):
            yy = yy[(xx < l) | (xx > r)]
            xx = xx[(xx < l) | (xx > r)]

        xx = np.concatenate(([minx], xx, [maxx]))
        yy = np.concatenate(([miny], yy, [maxy]))

        result = update_varied_params(result, fit(result, data=yy, x=xx, **fit_kwargs))

    for param in vary_bckg:
        result.params[param].vary = vary_bckg[param]
        result.params[param].stderr = bckg_stderr[param]

    return result