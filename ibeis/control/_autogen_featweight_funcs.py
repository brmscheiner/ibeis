# -*- coding: utf-8 -*-
"""
Autogenerated IBEISController functions

TemplateInfo:
    autogen_time = 11:48:39 2015/03/13
    autogen_key = featweight

ToRegenerate:
    python -m ibeis.templates.template_generator --key featweight --Tcfg with_web_api=False --diff
    python -m ibeis.templates.template_generator --key featweight --Tcfg with_web_api=False --write
"""
from __future__ import absolute_import, division, print_function
import functools  # NOQA
import six  # NOQA
from six.moves import map, range, zip  # NOQA
from ibeis import constants as const
import utool as ut
from ibeis.control import controller_inject
from ibeis.control import accessor_decors  # NOQA
print, print_, printDBG, rrr, profile = ut.inject(__name__, '[autogen_featweight]')

# Create dectorator to inject functions in this module into the IBEISController
CLASS_INJECT_KEY, register_ibs_method = controller_inject.make_ibs_register_decorator(__name__)
register_route = controller_inject.get_ibeis_flask_route(__name__)


def testdata_ibs(defaultdb='testdb1'):
    import ibeis
    ibs = ibeis.opendb(defaultdb=defaultdb)
    config2_ = None  # qreq_.qparams
    return ibs, config2_

# AUTOGENED CONSTANTS:
ANNOT_ROWID                 = 'annot_rowid'
CHIP_ROWID                  = 'chip_rowid'
CONFIG_ROWID                = 'config_rowid'
FEATURE_ROWID               = 'feature_rowid'
FEATWEIGHT_FORGROUND_WEIGHT = 'featweight_forground_weight'
FEATWEIGHT_ROWID            = 'featweight_rowid'
FEAT_ROWID                  = 'feature_rowid'


@register_ibs_method
def _get_all_featweight_rowids(ibs):
    """ all_featweight_rowids <- featweight.get_all_rowids()

    Returns:
        list_ (list): unfiltered featweight_rowids

    TemplateInfo:
        Tider_all_rowids
        tbl = featweight

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> ibs._get_all_featweight_rowids()
    """
    all_featweight_rowids = ibs.dbcache.get_all_rowids(
        const.FEATURE_WEIGHT_TABLE)
    return all_featweight_rowids


@register_ibs_method
def add_annot_featweights(ibs, aid_list, config2_=None):
    """ featweight_rowid_list <- annot.featweight.ensure(aid_list)

    Adds / ensures / computes a dependant property (convinience)

    Args:
        aid_list

    Returns:
        featweight_rowid_list

    TemplateInfo:
        Tadder_rl_dependant
        root = annot
        leaf = featweight

    Example:
        >>> # SLOW_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> aid_list = ibs._get_all_aids()[:2]
        >>> featweight_rowid_list = ibs.add_annot_featweights(aid_list, config2_=config2_)
        >>> assert len(featweight_rowid_list) == len(aid_list)
        >>> ut.assert_all_not_None(featweight_rowid_list)
    """
    feat_rowid_list = ibs.get_annot_feat_rowids(
        aid_list, config2_=config2_, ensure=True)
    featweight_rowid_list = add_feat_featweights(
        ibs, feat_rowid_list, config2_=config2_)
    return featweight_rowid_list


@register_ibs_method
def add_feat_featweights(ibs, feat_rowid_list, config2_=None, verbose=not ut.QUIET, return_num_dirty=False):
    """ feat.featweight.add(feat_rowid_list)

    CRITICAL FUNCTION MUST EXIST FOR ALL DEPENDANTS
    Adds / ensures / computes a dependant property

    Args:
         feat_rowid_list

    Returns:
        returns featweight_rowid_list of added (or already existing featweights)

    TemplateInfo:
        Tadder_pl_dependant
        parent = feat
        leaf = featweight

    Example0:
        >>> # SLOW_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> from ibeis import constants as const
        >>> aid_list = ibs.get_valid_aids(species=const.TEST_SPECIES.ZEB_PLAIN)[:2]
        >>> if 'annot' != 'feat':
        ...     feat_rowid_list = ibs.get_annot_feat_rowids(aid_list, config2_=config2_, ensure=True)
        >>> featweight_rowid_list = ibs.add_feat_featweights(feat_rowid_list, config2_=config2_)
        >>> assert len(featweight_rowid_list) == len(feat_rowid_list)
        >>> ut.assert_all_not_None(featweight_rowid_list)

    Example1:
        >>> # SLOW_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs('PZ_MTEST')
        >>> from ibeis import constants as const
        >>> aid_list = ibs.get_valid_aids(species=const.TEST_SPECIES.ZEB_PLAIN)[0:7]
        >>> if 'annot' != 'feat':
        ...     feat_rowid_list = ibs.get_annot_feat_rowids(aid_list, config2_=config2_, ensure=True)
        >>> sub_feat_rowid_list1 = feat_rowid_list[0:6]
        >>> sub_feat_rowid_list2 = feat_rowid_list[5:7]
        >>> sub_feat_rowid_list3 = feat_rowid_list[0:7]
        >>> sub_featweight_rowid_list1 = ibs.get_feat_featweight_rowids(sub_feat_rowid_list1, config2_=config2_, ensure=True)
        >>> ibs.get_feat_featweight_rowids(sub_feat_rowid_list1, config2_=config2_, ensure=True)
        >>> sub_featweight_rowid_list1, num_dirty0 = ibs.add_feat_featweights(sub_feat_rowid_list1, config2_=config2_, return_num_dirty=True)
        >>> assert num_dirty0 == 0
        >>> ut.assert_all_not_None(sub_featweight_rowid_list1)
        >>> ibs.delete_feat_featweight(sub_feat_rowid_list2)
        >>> #ibs.delete_feat_featweight(sub_feat_rowid_list2)?
        >>> sub_featweight_rowid_list3 = ibs.get_feat_featweight_rowids(sub_feat_rowid_list3, config2_=config2_, ensure=False)
        >>> # Only the last two should be None
        >>> ut.assert_all_not_None(sub_featweight_rowid_list3[0:5], 'sub_featweight_rowid_list3[0:5])')
        >>> ut.assert_eq(sub_featweight_rowid_list3[5:7], [None, None])
        >>> sub_featweight_rowid_list3_ensured, num_dirty1 = ibs.add_feat_featweights(sub_feat_rowid_list3, config2_=config2_,  return_num_dirty=True)
        >>> ut.assert_eq(num_dirty1, 2, 'Only two params should have been computed here')
        >>> ut.assert_all_not_None(sub_featweight_rowid_list3_ensured)
    """
    from ibeis.algo.preproc import preproc_featweight
    ut.assert_all_not_None(feat_rowid_list, ' feat_rowid_list')
    # Get requested configuration id
    config_rowid = ibs.get_featweight_config_rowid(config2_=config2_)
    # Find leaf rowids that need to be computed
    initial_featweight_rowid_list = get_feat_featweight_rowids_(
        ibs, feat_rowid_list, config2_=config2_)
    # Get corresponding "dirty" parent rowids
    isdirty_list = ut.flag_None_items(initial_featweight_rowid_list)
    dirty_feat_rowid_list = ut.compress(feat_rowid_list, isdirty_list)
    num_dirty = len(dirty_feat_rowid_list)
    num_total = len(feat_rowid_list)
    if num_dirty > 0:
        if verbose:
            fmtstr = '[add_feat_featweights] adding %d / %d new featweight for config_rowid=%r'
            print(fmtstr % (num_dirty, num_total, config_rowid))
        # Dependant columns do not need true from_superkey getters.
        # We can use the Tgetter_pl_dependant_rowids_ instead
        get_rowid_from_superkey = functools.partial(
            ibs.get_feat_featweight_rowids_, config2_=config2_)
        proptup_gen = preproc_featweight.generate_featweight_properties(
            ibs, dirty_feat_rowid_list, config2_=config2_)
        dirty_params_iter = (
            (feat_rowid, config_rowid, fgweight)
            for feat_rowid, (fgweight,) in
            zip(dirty_feat_rowid_list, proptup_gen)
        )
        colnames = [
            'feature_rowid', 'config_rowid', 'featweight_forground_weight']
        #featweight_rowid_list = ibs.dbcache.add_cleanly(const.FEATURE_WEIGHT_TABLE, colnames, dirty_params_iter, get_rowid_from_superkey)
        ibs.dbcache._add(
            const.FEATURE_WEIGHT_TABLE, colnames, dirty_params_iter)
        # Now that the dirty params are added get the correct order of rowids
        featweight_rowid_list = get_rowid_from_superkey(feat_rowid_list)
    else:
        featweight_rowid_list = initial_featweight_rowid_list
    if return_num_dirty:
        return featweight_rowid_list, num_dirty
    return featweight_rowid_list


@register_ibs_method
def add_featweight(ibs, feature_rowid_list, config_rowid_list, fgweight_list):
    """
    Returns:
        returns featweight_rowid_list of added (or already existing featweights)

    TemplateInfo:
        Tadder_native
        tbl = featweight
    """
    # WORK IN PROGRESS
    colnames = (FEATURE_ROWID, CONFIG_ROWID, FEATWEIGHT_FORGROUND_WEIGHT,)
    params_iter = (
        (feature_rowid, config_rowid, fgweight,)
        for (feature_rowid, config_rowid, fgweight,) in
        zip(feature_rowid_list, config_rowid_list, fgweight_list)
    )
    get_rowid_from_superkey = ibs.get_featweight_rowid_from_superkey
    # FIXME: encode superkey paramx
    superkey_paramx = (0, 1)
    featweight_rowid_list = ibs.dbcache.add_cleanly(
        const.FEATURE_WEIGHT_TABLE, colnames, params_iter, get_rowid_from_superkey, superkey_paramx)
    return featweight_rowid_list


@register_ibs_method
def delete_annot_featweight(ibs, aid_list, config2_=None):
    """ annot.featweight.delete(aid_list)

    Args:
        aid_list

    TemplateInfo:
        Tdeleter_rl_depenant
        root = annot
        leaf = featweight

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> aid_list = ibs._get_all_aids()[:1]
        >>> # Ensure there are  some leafs to delete
        >>> featweight_rowid_list = ibs.get_annot_featweight_rowids(aid_list, config2_=config2_, ensure=True)
        >>> num_deleted1 = ibs.delete_annot_featweight(aid_list, config2_=config2_)
        >>> num_deleted2 = ibs.delete_annot_featweight(aid_list, config2_=config2_)
        >>> # The first delete should remove everything
        >>> ut.assert_eq(num_deleted1, len(featweight_rowid_list))
        >>> # The second delete should have removed nothing
        >>> ut.assert_eq(num_deleted2, 0)
    """
    if ut.VERBOSE:
        print('[ibs] deleting %d annots leaf nodes' % len(aid_list))
    # Delete any dependants
    _featweight_rowid_list = ibs.get_annot_featweight_rowids(
        aid_list, config2_=config2_, ensure=False)
    featweight_rowid_list = ut.filter_Nones(_featweight_rowid_list)
    num_deleted = ibs.delete_featweight(featweight_rowid_list)
    return num_deleted


@register_ibs_method
def delete_feat_featweight(ibs, feat_rowid_list, config2_=None):
    """ feat.featweight.delete(feat_rowid_list)

    Args:
        feat_rowid_list

    Returns:
         int: num_deleted

    TemplateInfo:
        Tdeleter_rl_depenant
        parent = feat
        leaf = featweight

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> feat_rowid_list = ibs._get_all_feat_rowids()[:2]
        >>> ibs.delete_feat_featweight(feat_rowid_list, config2_=config2_)
    """
    if ut.VERBOSE:
        print('[ibs] deleting %d feats leaf nodes' % len(feat_rowid_list))
    # Delete any dependants
    _featweight_rowid_list = ibs.get_feat_featweight_rowids(
        feat_rowid_list, config2_=config2_, ensure=False)
    featweight_rowid_list = ut.filter_Nones(_featweight_rowid_list)
    num_deleted = ibs.delete_featweight(featweight_rowid_list)
    return num_deleted


@register_ibs_method
def delete_featweight(ibs, featweight_rowid_list, config2_=None):
    """ featweight.delete(featweight_rowid_list)

    delete featweight rows

    Args:
        featweight_rowid_list

    Returns:
        int: num_deleted

    TemplateInfo:
        Tdeleter_native_tbl
        tbl = featweight

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> featweight_rowid_list = ibs._get_all_featweight_rowids()[:2]
        >>> ibs.delete_featweight(featweight_rowid_list)
    """
    from ibeis.algo.preproc import preproc_featweight
    if ut.VERBOSE:
        print('[ibs] deleting %d featweight rows' % len(featweight_rowid_list))
    # Prepare: Delete externally stored data (if any)
    preproc_featweight.on_delete(ibs, featweight_rowid_list, config2_=config2_)
    # Finalize: Delete self
    ibs.dbcache.delete_rowids(const.FEATURE_WEIGHT_TABLE, featweight_rowid_list)
    num_deleted = len(featweight_rowid_list)
    return num_deleted


@register_ibs_method
def get_annot_featweight_all_rowids(ibs, aid_list, eager=True, nInput=None):
    """ featweight_rowid_list <- annot.featweight.all_rowids([aid_list])

    Gets featweight rowids of annot under the current state configuration.

    Args:
        aid_list (list):

    Returns:
        list: featweight_rowid_list

    TemplateInfo:
        Tider_rl_dependant_all_rowids
        root = annot
        leaf = featweight
    """
    # FIXME: broken
    colnames = (FEAT_ROWID,)
    featweight_rowid_list = ibs.dbcache.get(
        const.FEATURE_WEIGHT_TABLE, colnames, aid_list,
        id_colname=ANNOT_ROWID, eager=eager, nInput=nInput)
    return featweight_rowid_list


@register_ibs_method
def get_annot_featweight_rowids(ibs, aid_list, config2_=None, ensure=True, eager=True, nInput=None):
    """ featweight_rowid_list <- annot.featweight.rowids[aid_list]

    Get featweight rowids of annot under the current state configuration.

    Args:
        aid_list (list):

    Returns:
        list: featweight_rowid_list

    TemplateInfo:
        Tgetter_rl_dependant_rowids
        root        = annot
        leaf_parent = feat
        leaf        = featweight

    Example:
        >>> # SLOW_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> aid_list = ibs._get_all_aids()
        >>> featweight_rowid_list1 = ibs.get_annot_featweight_rowids(aid_list, config2_, ensure=False)
        >>> featweight_rowid_list2 = ibs.get_annot_featweight_rowids(aid_list, config2_, ensure=True)
        >>> featweight_rowid_list3 = ibs.get_annot_featweight_rowids(aid_list, config2_, ensure=False)
        >>> print(featweight_rowid_list1)
        >>> print(featweight_rowid_list2)
        >>> print(featweight_rowid_list3)
    """
    # Get leaf_parent rowids
    feat_rowid_list = ibs.get_annot_feat_rowids(
        aid_list, config2_=config2_, ensure=ensure)
    featweight_rowid_list = get_feat_featweight_rowids(
        ibs, feat_rowid_list, config2_=config2_, ensure=ensure)
    return featweight_rowid_list


@register_ibs_method
def get_annot_fgweights(ibs, aid_list, config2_=None, ensure=True):
    """ featweight_rowid_list <- annot.featweight.fgweights[aid_list]

    Get fgweight data of the annot table using the dependant featweight table

    Args:
        aid_list (list):

    Returns:
        list: fgweight_list

    TemplateInfo:
        Tgetter_rl_pclines_dependant_column
        root = annot
        col  = fgweight
        leaf = featweight
    """
    chip_rowid_list = ibs.get_annot_chip_rowids(
        aid_list, config2_=config2_, ensure=ensure)
    feat_rowid_list = ibs.get_chip_feat_rowid(
        chip_rowid_list, config2_=config2_, ensure=ensure)
    featweight_rowid_list = ibs.get_feat_featweight_rowids(
        feat_rowid_list, config2_=config2_, ensure=ensure)
    fgweight_list = ibs.get_featweight_fgweight(featweight_rowid_list)
    return fgweight_list


@register_ibs_method
def get_feat_featweight_rowids(ibs, feat_rowid_list, config2_=None, ensure=True, eager=True, nInput=None):
    """ featweight_rowid_list <- feat.featweight.rowids[feat_rowid_list]

    get featweight rowids of feat under the current state configuration
    if ensure is True, this function is equivalent to add_feat_featweights

    Args:
        feat_rowid_list (list):
        ensure (bool): default false

    Returns:
        list: featweight_rowid_list

    TemplateInfo:
        Tgetter_pl_dependant_rowids
        parent = feat
        leaf = featweight

    Timeit:
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> # Test to see if there is any overhead to injected vs native functions
        >>> %timeit get_feat_featweight_rowids(ibs, feat_rowid_list)
        >>> %timeit ibs.get_feat_featweight_rowids(feat_rowid_list)

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> feat_rowid_list = ibs._get_all_feat_rowids()
        >>> ensure = False
        >>> featweight_rowid_list = ibs.get_feat_featweight_rowids(feat_rowid_list, config2_, ensure)
        >>> assert len(featweight_rowid_list) == len(feat_rowid_list)
    """
    if ensure:
        featweight_rowid_list = add_feat_featweights(
            ibs, feat_rowid_list, config2_=config2_)
    else:
        featweight_rowid_list = get_feat_featweight_rowids_(
            ibs, feat_rowid_list, config2_=config2_, eager=eager, nInput=nInput)
    return featweight_rowid_list


@register_ibs_method
def get_feat_featweight_rowids_(ibs, feat_rowid_list, config2_=None, eager=True, nInput=None):
    """
    equivalent to get_feat_featweight_rowids_ except ensure is constrained
    to be False.

    Also you save a stack frame because get_feat_featweight_rowids just
    calls this function if ensure is False

    TemplateInfo:
        Tgetter_pl_dependant_rowids_
    """
    colnames = (FEATWEIGHT_ROWID,)
    config_rowid = ibs.get_featweight_config_rowid(config2_=config2_)
    andwhere_colnames = (FEAT_ROWID, CONFIG_ROWID,)
    params_iter = ((feat_rowid, config_rowid,)
                   for feat_rowid in feat_rowid_list)
    featweight_rowid_list = ibs.dbcache.get_where2(
        const.FEATURE_WEIGHT_TABLE, colnames, params_iter, andwhere_colnames, eager=eager, nInput=nInput)
    return featweight_rowid_list


@register_ibs_method
def get_featweight_config_rowid(ibs, config2_=None):
    """ featweight_cfg_rowid = featweight.config_rowid()

    returns config_rowid of the current configuration
    Config rowids are always ensured

    Returns:
        featweight_cfg_rowid

    TemplateInfo:
        Tcfg_rowid_getter
        leaf = featweight

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> featweight_cfg_rowid = ibs.get_featweight_config_rowid()
    """
    if config2_ is not None:
        #featweight_cfg_suffix = config2_.qparams.featweight_cfgstr
        featweight_cfg_suffix = config2_.get('featweight_cfgstr')
        assert featweight_cfg_suffix is not None
        # TODO store config_rowid in qparams
    else:
        featweight_cfg_suffix = ibs.cfg.featweight_cfg.get_cfgstr()
    featweight_cfg_rowid = ibs.add_config(featweight_cfg_suffix)
    return featweight_cfg_rowid


@register_ibs_method
def get_featweight_feat_rowid(ibs, featweight_rowid_list, eager=True, nInput=None):
    """ feat_rowid_list <- featweight.feat_rowid[featweight_rowid_list]

    gets data from the "native" column "feat_rowid" in the "featweight" table

    Args:
        featweight_rowid_list (list):

    Returns:
        list: feat_rowid_list

    TemplateInfo:
        Tgetter_table_column
        col = feat_rowid
        tbl = featweight

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> featweight_rowid_list = ibs._get_all_featweight_rowids()
        >>> eager = True
        >>> feat_rowid_list = ibs.get_featweight_feat_rowid(featweight_rowid_list, eager=eager)
        >>> assert len(featweight_rowid_list) == len(feat_rowid_list)
    """
    id_iter = featweight_rowid_list
    colnames = (FEATURE_ROWID,)
    feat_rowid_list = ibs.dbcache.get(
        const.FEATURE_WEIGHT_TABLE, colnames, id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return feat_rowid_list


@register_ibs_method
def get_featweight_fgweight(ibs, featweight_rowid_list, eager=True, nInput=None):
    """ fgweight_list <- featweight.fgweight[featweight_rowid_list]

    gets data from the "native" column "fgweight" in the "featweight" table

    Args:
        featweight_rowid_list (list):

    Returns:
        list: fgweight_list

    TemplateInfo:
        Tgetter_table_column
        col = fgweight
        tbl = featweight

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_featweight_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_ibs()
        >>> featweight_rowid_list = ibs._get_all_featweight_rowids()
        >>> eager = True
        >>> fgweight_list = ibs.get_featweight_fgweight(featweight_rowid_list, eager=eager)
        >>> assert len(featweight_rowid_list) == len(fgweight_list)
    """
    id_iter = featweight_rowid_list
    colnames = (FEATWEIGHT_FORGROUND_WEIGHT,)
    fgweight_list = ibs.dbcache.get(
        const.FEATURE_WEIGHT_TABLE, colnames, id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return fgweight_list


@register_ibs_method
def get_featweight_rowid_from_superkey(ibs, feature_rowid_list, config_rowid_list, eager=True, nInput=None):
    """ featweight_rowid_list <- featweight[feature_rowid_list, config_rowid_list]

    Args:
        superkey lists: feature_rowid_list, config_rowid_list

    Returns:
        featweight_rowid_list

    TemplateInfo:
        Tgetter_native_rowid_from_superkey
        tbl = featweight
    """
    colnames = (FEATWEIGHT_ROWID,)
    # FIXME: col_rowid is not correct
    params_iter = zip(feature_rowid_list, config_rowid_list)
    andwhere_colnames = [FEATURE_ROWID, CONFIG_ROWID]
    featweight_rowid_list = ibs.dbcache.get_where2(
        const.FEATURE_WEIGHT_TABLE, colnames, params_iter, andwhere_colnames, eager=eager, nInput=nInput)
    return featweight_rowid_list


@register_ibs_method
def set_featweight_fgweight(ibs, featweight_rowid_list, fgweight_list, duplicate_behavior='error'):
    """ fgweight_list -> featweight.fgweight[featweight_rowid_list]

    Args:
        featweight_rowid_list
        fgweight_list

    TemplateInfo:
        Tsetter_native_column
        tbl = featweight
        col = fgweight
    """
    id_iter = featweight_rowid_list
    colnames = (FEATWEIGHT_FORGROUND_WEIGHT,)
    ibs.dbcache.set(const.FEATURE_WEIGHT_TABLE, colnames,
                    fgweight_list, id_iter, duplicate_behavior=duplicate_behavior)


if __name__ == '__main__':
    """
    CommandLine:
        python -m ibeis.control._autogen_featweight_funcs
        python -m ibeis.control._autogen_featweight_funcs --allexamples
    """
    import multiprocessing
    multiprocessing.freeze_support()
    import utool as ut
    ut.doctest_funcs()
