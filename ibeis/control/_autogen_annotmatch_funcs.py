# -*- coding: utf-8 -*-
"""
Autogenerated IBEISController functions

TemplateInfo:
    autogen_time = 11:34:25 2016/01/05
    autogen_key = annotmatch

ToRegenerate:
    python -m ibeis.templates.template_generator --key annotmatch --Tcfg with_web_api=False with_api_cache=False with_deleters=True no_extern_deleters=True --diff
    python -m ibeis.templates.template_generator --key annotmatch --Tcfg with_web_api=False with_api_cache=False with_deleters=True no_extern_deleters=True --write
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import functools  # NOQA
import six  # NOQA
from six.moves import map, range, zip  # NOQA
from ibeis import constants as const
import utool as ut
from ibeis.control import controller_inject
from ibeis.control import accessor_decors  # NOQA
print, rrr, profile = ut.inject2(__name__)

# Create dectorator to inject functions in this module into the IBEISController
CLASS_INJECT_KEY, register_ibs_method = controller_inject.make_ibs_register_decorator(__name__)


register_api   = controller_inject.get_ibeis_flask_api(__name__)
register_route = controller_inject.get_ibeis_flask_route(__name__)


def testdata_annotmatch(defaultdb='testdb1'):
    import ibeis
    ibs = ibeis.opendb(defaultdb=defaultdb)
    config2_ = None  # qreq_.qparams
    #from ibeis.hots import query_config
    #config2_ = query_config.QueryParams(cfgdict=dict())
    return ibs, config2_

# AUTOGENED CONSTANTS:
ANNOTMATCH_CONFIDENCE         = 'annotmatch_confidence'
ANNOTMATCH_PAIRWISE_PROB      = 'annotmatch_pairwise_prob'
ANNOTMATCH_POSIXTIME_MODIFIED = 'annotmatch_posixtime_modified'
ANNOTMATCH_REVIEWED           = 'annotmatch_reviewed'
ANNOTMATCH_REVIEWER           = 'annotmatch_reviewer'
ANNOTMATCH_ROWID              = 'annotmatch_rowid'
ANNOTMATCH_TAG_TEXT           = 'annotmatch_tag_text'
ANNOTMATCH_TRUTH              = 'annotmatch_truth'
ANNOT_ROWID1                  = 'annot_rowid1'
ANNOT_ROWID2                  = 'annot_rowid2'
CONFIG_HASHID                 = 'config_hashid'
CONFIG_ROWID                  = 'config_rowid'
FEATWEIGHT_ROWID              = 'featweight_rowid'


@register_ibs_method
def _get_all_annotmatch_rowids(ibs):
    r""" all_annotmatch_rowids <- annotmatch.get_all_rowids()

    Returns:
        list_ (list): unfiltered annotmatch_rowids

    TemplateInfo:
        Tider_all_rowids
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> ibs._get_all_annotmatch_rowids()
    """
    all_annotmatch_rowids = ibs.db.get_all_rowids(const.ANNOTMATCH_TABLE)
    return all_annotmatch_rowids


@register_ibs_method
def add_annotmatch(ibs, aid1_list, aid2_list, annotmatch_truth_list=None, annotmatch_confidence_list=None, annotmatch_tag_text_list=None, annotmatch_reviewed_list=None, annotmatch_reviewer_list=None, annotmatch_posixtime_modified_list=None, annotmatch_pairwise_prob_list=None, config_hashid_list=None):
    r"""
    Returns:
        returns annotmatch_rowid_list of added (or already existing annotmatchs)

    TemplateInfo:
        Tadder_native
        tbl = annotmatch
    """
    # WORK IN PROGRESS
    colnames = (ANNOT_ROWID1, ANNOT_ROWID2, ANNOTMATCH_TRUTH, ANNOTMATCH_CONFIDENCE, ANNOTMATCH_TAG_TEXT,
                ANNOTMATCH_REVIEWED, ANNOTMATCH_REVIEWER, ANNOTMATCH_POSIXTIME_MODIFIED, ANNOTMATCH_PAIRWISE_PROB, CONFIG_HASHID,)
    if annotmatch_truth_list is None:
        annotmatch_truth_list = [None] * len(aid1_list)
    if annotmatch_confidence_list is None:
        annotmatch_confidence_list = [None] * len(aid1_list)
    if annotmatch_tag_text_list is None:
        annotmatch_tag_text_list = [None] * len(aid1_list)
    if annotmatch_reviewed_list is None:
        annotmatch_reviewed_list = [None] * len(aid1_list)
    if annotmatch_reviewer_list is None:
        annotmatch_reviewer_list = [None] * len(aid1_list)
    if annotmatch_posixtime_modified_list is None:
        annotmatch_posixtime_modified_list = [None] * len(aid1_list)
    if annotmatch_pairwise_prob_list is None:
        annotmatch_pairwise_prob_list = [None] * len(aid1_list)
    if config_hashid_list is None:
        config_hashid_list = [None] * len(aid1_list)
    params_iter = (
        (aid1, aid2, annotmatch_truth, annotmatch_confidence, annotmatch_tag_text, annotmatch_reviewed,
         annotmatch_reviewer, annotmatch_posixtime_modified, annotmatch_pairwise_prob, config_hashid,)
        for (aid1, aid2, annotmatch_truth, annotmatch_confidence, annotmatch_tag_text, annotmatch_reviewed, annotmatch_reviewer, annotmatch_posixtime_modified, annotmatch_pairwise_prob, config_hashid,) in
        zip(aid1_list, aid2_list, annotmatch_truth_list, annotmatch_confidence_list, annotmatch_tag_text_list, annotmatch_reviewed_list,
            annotmatch_reviewer_list, annotmatch_posixtime_modified_list, annotmatch_pairwise_prob_list, config_hashid_list)
    )
    get_rowid_from_superkey = ibs.get_annotmatch_rowid_from_superkey
    # FIXME: encode superkey paramx
    superkey_paramx = (0, 1)
    annotmatch_rowid_list = ibs.db.add_cleanly(
        const.ANNOTMATCH_TABLE, colnames, params_iter, get_rowid_from_superkey, superkey_paramx)
    return annotmatch_rowid_list


@register_ibs_method
def delete_annotmatch(ibs, annotmatch_rowid_list, config2_=None):
    r""" annotmatch.delete(annotmatch_rowid_list)

    delete annotmatch rows

    Args:
        annotmatch_rowid_list

    Returns:
        int: num_deleted

    TemplateInfo:
        Tdeleter_native_tbl
        tbl = annotmatch

    Example:
        >>> # DISABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()[:2]
        >>> num_deleted = ibs.delete_annotmatch(annotmatch_rowid_list)
        >>> print('num_deleted = %r' % (num_deleted,))
    """
    #from ibeis.algo.preproc import preproc_annotmatch
    # NO EXTERN IMPORT
    if ut.VERBOSE:
        print('[ibs] deleting %d annotmatch rows' % len(annotmatch_rowid_list))
    # Prepare: Delete externally stored data (if any)
    #preproc_annotmatch.on_delete(ibs, annotmatch_rowid_list, config2_=config2_)
    # NO EXTERN DELETE
    # Finalize: Delete self
    ibs.db.delete_rowids(const.ANNOTMATCH_TABLE, annotmatch_rowid_list)
    num_deleted = len(ut.filter_Nones(annotmatch_rowid_list))
    return num_deleted


@register_ibs_method
@accessor_decors.getter_1to1
def get_annotmatch_aid1(ibs, annotmatch_rowid_list, eager=True, nInput=None):
    r""" aid1_list <- annotmatch.aid1[annotmatch_rowid_list]

    gets data from the "native" column "aid1" in the "annotmatch" table

    Args:
        annotmatch_rowid_list (list):

    Returns:
        list: aid1_list

    TemplateInfo:
        Tgetter_table_column
        col = aid1
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()
        >>> eager = True
        >>> aid1_list = ibs.get_annotmatch_aid1(annotmatch_rowid_list, eager=eager)
        >>> assert len(annotmatch_rowid_list) == len(aid1_list)
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOT_ROWID1,)
    aid1_list = ibs.db.get(const.ANNOTMATCH_TABLE, colnames,
                           id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return aid1_list


@register_ibs_method
@accessor_decors.getter_1to1
def get_annotmatch_aid2(ibs, annotmatch_rowid_list, eager=True, nInput=None):
    r""" aid2_list <- annotmatch.aid2[annotmatch_rowid_list]

    gets data from the "native" column "aid2" in the "annotmatch" table

    Args:
        annotmatch_rowid_list (list):

    Returns:
        list: aid2_list

    TemplateInfo:
        Tgetter_table_column
        col = aid2
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()
        >>> eager = True
        >>> aid2_list = ibs.get_annotmatch_aid2(annotmatch_rowid_list, eager=eager)
        >>> assert len(annotmatch_rowid_list) == len(aid2_list)
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOT_ROWID2,)
    aid2_list = ibs.db.get(const.ANNOTMATCH_TABLE, colnames,
                           id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return aid2_list


@register_ibs_method
@accessor_decors.getter_1to1
def get_annotmatch_confidence(ibs, annotmatch_rowid_list, eager=True, nInput=None):
    r""" annotmatch_confidence_list <- annotmatch.annotmatch_confidence[annotmatch_rowid_list]

    gets data from the "native" column "annotmatch_confidence" in the "annotmatch" table

    Args:
        annotmatch_rowid_list (list):

    Returns:
        list: annotmatch_confidence_list

    TemplateInfo:
        Tgetter_table_column
        col = annotmatch_confidence
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()
        >>> eager = True
        >>> annotmatch_confidence_list = ibs.get_annotmatch_confidence(annotmatch_rowid_list, eager=eager)
        >>> assert len(annotmatch_rowid_list) == len(annotmatch_confidence_list)
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_CONFIDENCE,)
    annotmatch_confidence_list = ibs.db.get(
        const.ANNOTMATCH_TABLE, colnames, id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return annotmatch_confidence_list


@register_ibs_method
@accessor_decors.getter_1to1
def get_annotmatch_config_hashid(ibs, annotmatch_rowid_list, eager=True, nInput=None):
    r""" config_hashid_list <- annotmatch.config_hashid[annotmatch_rowid_list]

    gets data from the "native" column "config_hashid" in the "annotmatch" table

    Args:
        annotmatch_rowid_list (list):

    Returns:
        list: config_hashid_list

    TemplateInfo:
        Tgetter_table_column
        col = config_hashid
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()
        >>> eager = True
        >>> config_hashid_list = ibs.get_annotmatch_config_hashid(annotmatch_rowid_list, eager=eager)
        >>> assert len(annotmatch_rowid_list) == len(config_hashid_list)
    """
    id_iter = annotmatch_rowid_list
    colnames = (CONFIG_HASHID,)
    config_hashid_list = ibs.db.get(
        const.ANNOTMATCH_TABLE, colnames, id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return config_hashid_list


@register_ibs_method
@accessor_decors.getter_1to1
def get_annotmatch_pairwise_prob(ibs, annotmatch_rowid_list, eager=True, nInput=None):
    r""" annotmatch_pairwise_prob_list <- annotmatch.annotmatch_pairwise_prob[annotmatch_rowid_list]

    gets data from the "native" column "annotmatch_pairwise_prob" in the "annotmatch" table

    Args:
        annotmatch_rowid_list (list):

    Returns:
        list: annotmatch_pairwise_prob_list

    TemplateInfo:
        Tgetter_table_column
        col = annotmatch_pairwise_prob
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()
        >>> eager = True
        >>> annotmatch_pairwise_prob_list = ibs.get_annotmatch_pairwise_prob(annotmatch_rowid_list, eager=eager)
        >>> assert len(annotmatch_rowid_list) == len(annotmatch_pairwise_prob_list)
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_PAIRWISE_PROB,)
    annotmatch_pairwise_prob_list = ibs.db.get(
        const.ANNOTMATCH_TABLE, colnames, id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return annotmatch_pairwise_prob_list


@register_ibs_method
@accessor_decors.getter_1to1
def get_annotmatch_posixtime_modified(ibs, annotmatch_rowid_list, eager=True, nInput=None):
    r""" annotmatch_posixtime_modified_list <- annotmatch.annotmatch_posixtime_modified[annotmatch_rowid_list]

    gets data from the "native" column "annotmatch_posixtime_modified" in the "annotmatch" table

    Args:
        annotmatch_rowid_list (list):

    Returns:
        list: annotmatch_posixtime_modified_list

    TemplateInfo:
        Tgetter_table_column
        col = annotmatch_posixtime_modified
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()
        >>> eager = True
        >>> annotmatch_posixtime_modified_list = ibs.get_annotmatch_posixtime_modified(annotmatch_rowid_list, eager=eager)
        >>> assert len(annotmatch_rowid_list) == len(annotmatch_posixtime_modified_list)
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_POSIXTIME_MODIFIED,)
    annotmatch_posixtime_modified_list = ibs.db.get(
        const.ANNOTMATCH_TABLE, colnames, id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return annotmatch_posixtime_modified_list


@register_ibs_method
@accessor_decors.getter_1to1
def get_annotmatch_reviewed(ibs, annotmatch_rowid_list, eager=True, nInput=None):
    r""" annotmatch_reviewed_list <- annotmatch.annotmatch_reviewed[annotmatch_rowid_list]

    gets data from the "native" column "annotmatch_reviewed" in the "annotmatch" table

    Args:
        annotmatch_rowid_list (list):

    Returns:
        list: annotmatch_reviewed_list

    TemplateInfo:
        Tgetter_table_column
        col = annotmatch_reviewed
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()
        >>> eager = True
        >>> annotmatch_reviewed_list = ibs.get_annotmatch_reviewed(annotmatch_rowid_list, eager=eager)
        >>> assert len(annotmatch_rowid_list) == len(annotmatch_reviewed_list)
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_REVIEWED,)
    annotmatch_reviewed_list = ibs.db.get(
        const.ANNOTMATCH_TABLE, colnames, id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return annotmatch_reviewed_list


@register_ibs_method
@accessor_decors.getter_1to1
def get_annotmatch_reviewer(ibs, annotmatch_rowid_list, eager=True, nInput=None):
    r""" annotmatch_reviewer_list <- annotmatch.annotmatch_reviewer[annotmatch_rowid_list]

    gets data from the "native" column "annotmatch_reviewer" in the "annotmatch" table

    Args:
        annotmatch_rowid_list (list):

    Returns:
        list: annotmatch_reviewer_list

    TemplateInfo:
        Tgetter_table_column
        col = annotmatch_reviewer
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()
        >>> eager = True
        >>> annotmatch_reviewer_list = ibs.get_annotmatch_reviewer(annotmatch_rowid_list, eager=eager)
        >>> assert len(annotmatch_rowid_list) == len(annotmatch_reviewer_list)
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_REVIEWER,)
    annotmatch_reviewer_list = ibs.db.get(
        const.ANNOTMATCH_TABLE, colnames, id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return annotmatch_reviewer_list


@register_ibs_method
@accessor_decors.getter_1to1
def get_annotmatch_rowid(ibs, annotmatch_rowid_list, eager=True, nInput=None):
    r""" annotmatch_rowid_list <- annotmatch.annotmatch_rowid[annotmatch_rowid_list]

    gets data from the "native" column "annotmatch_rowid" in the "annotmatch" table

    Args:
        annotmatch_rowid_list (list):

    Returns:
        list: annotmatch_rowid_list

    TemplateInfo:
        Tgetter_table_column
        col = annotmatch_rowid
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()
        >>> eager = True
        >>> annotmatch_rowid_list = ibs.get_annotmatch_rowid(annotmatch_rowid_list, eager=eager)
        >>> assert len(annotmatch_rowid_list) == len(annotmatch_rowid_list)
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_ROWID,)
    annotmatch_rowid_list = ibs.db.get(
        const.ANNOTMATCH_TABLE, colnames, id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return annotmatch_rowid_list


@register_ibs_method
def get_annotmatch_rowid_from_superkey(ibs, aid1_list, aid2_list, eager=True, nInput=None):
    r""" annotmatch_rowid_list <- annotmatch[aid1_list, aid2_list]

    Args:
        superkey lists: aid1_list, aid2_list

    Returns:
        annotmatch_rowid_list

    TemplateInfo:
        Tgetter_native_rowid_from_superkey
        tbl = annotmatch
    """
    colnames = (ANNOTMATCH_ROWID,)
    # FIXME: col_rowid is not correct
    params_iter = zip(aid1_list, aid2_list)
    andwhere_colnames = [ANNOT_ROWID1, ANNOT_ROWID2]
    annotmatch_rowid_list = ibs.db.get_where2(
        const.ANNOTMATCH_TABLE, colnames, params_iter, andwhere_colnames, eager=eager, nInput=nInput)
    return annotmatch_rowid_list


@register_ibs_method
@accessor_decors.getter_1to1
def get_annotmatch_tag_text(ibs, annotmatch_rowid_list, eager=True, nInput=None):
    r""" annotmatch_tag_text_list <- annotmatch.annotmatch_tag_text[annotmatch_rowid_list]

    gets data from the "native" column "annotmatch_tag_text" in the "annotmatch" table

    Args:
        annotmatch_rowid_list (list):

    Returns:
        list: annotmatch_tag_text_list

    TemplateInfo:
        Tgetter_table_column
        col = annotmatch_tag_text
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()
        >>> eager = True
        >>> annotmatch_tag_text_list = ibs.get_annotmatch_tag_text(annotmatch_rowid_list, eager=eager)
        >>> assert len(annotmatch_rowid_list) == len(annotmatch_tag_text_list)
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_TAG_TEXT,)
    annotmatch_tag_text_list = ibs.db.get(
        const.ANNOTMATCH_TABLE, colnames, id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return annotmatch_tag_text_list


@register_ibs_method
@accessor_decors.getter_1to1
def get_annotmatch_truth(ibs, annotmatch_rowid_list, eager=True, nInput=None):
    r""" annotmatch_truth_list <- annotmatch.annotmatch_truth[annotmatch_rowid_list]

    gets data from the "native" column "annotmatch_truth" in the "annotmatch" table

    Args:
        annotmatch_rowid_list (list):

    Returns:
        list: annotmatch_truth_list

    TemplateInfo:
        Tgetter_table_column
        col = annotmatch_truth
        tbl = annotmatch

    Example:
        >>> # ENABLE_DOCTEST
        >>> from ibeis.control._autogen_annotmatch_funcs import *  # NOQA
        >>> ibs, config2_ = testdata_annotmatch()
        >>> annotmatch_rowid_list = ibs._get_all_annotmatch_rowids()
        >>> eager = True
        >>> annotmatch_truth_list = ibs.get_annotmatch_truth(annotmatch_rowid_list, eager=eager)
        >>> assert len(annotmatch_rowid_list) == len(annotmatch_truth_list)
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_TRUTH,)
    annotmatch_truth_list = ibs.db.get(
        const.ANNOTMATCH_TABLE, colnames, id_iter, id_colname='rowid', eager=eager, nInput=nInput)
    return annotmatch_truth_list


@register_ibs_method
@accessor_decors.setter
def set_annotmatch_confidence(ibs, annotmatch_rowid_list, annotmatch_confidence_list, duplicate_behavior='error'):
    r""" annotmatch_confidence_list -> annotmatch.annotmatch_confidence[annotmatch_rowid_list]

    Args:
        annotmatch_rowid_list
        annotmatch_confidence_list

    TemplateInfo:
        Tsetter_native_column
        tbl = annotmatch
        col = annotmatch_confidence
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_CONFIDENCE,)
    ibs.db.set(const.ANNOTMATCH_TABLE, colnames, annotmatch_confidence_list,
               id_iter, duplicate_behavior=duplicate_behavior)


@register_ibs_method
@accessor_decors.setter
def set_annotmatch_config_hashid(ibs, annotmatch_rowid_list, config_hashid_list, duplicate_behavior='error'):
    r""" config_hashid_list -> annotmatch.config_hashid[annotmatch_rowid_list]

    Args:
        annotmatch_rowid_list
        config_hashid_list

    TemplateInfo:
        Tsetter_native_column
        tbl = annotmatch
        col = config_hashid
    """
    id_iter = annotmatch_rowid_list
    colnames = (CONFIG_HASHID,)
    ibs.db.set(const.ANNOTMATCH_TABLE, colnames, config_hashid_list,
               id_iter, duplicate_behavior=duplicate_behavior)


@register_ibs_method
@accessor_decors.setter
def set_annotmatch_pairwise_prob(ibs, annotmatch_rowid_list, annotmatch_pairwise_prob_list, duplicate_behavior='error'):
    r""" annotmatch_pairwise_prob_list -> annotmatch.annotmatch_pairwise_prob[annotmatch_rowid_list]

    Args:
        annotmatch_rowid_list
        annotmatch_pairwise_prob_list

    TemplateInfo:
        Tsetter_native_column
        tbl = annotmatch
        col = annotmatch_pairwise_prob
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_PAIRWISE_PROB,)
    ibs.db.set(const.ANNOTMATCH_TABLE, colnames, annotmatch_pairwise_prob_list,
               id_iter, duplicate_behavior=duplicate_behavior)


@register_ibs_method
@accessor_decors.setter
def set_annotmatch_posixtime_modified(ibs, annotmatch_rowid_list, annotmatch_posixtime_modified_list, duplicate_behavior='error'):
    r""" annotmatch_posixtime_modified_list -> annotmatch.annotmatch_posixtime_modified[annotmatch_rowid_list]

    Args:
        annotmatch_rowid_list
        annotmatch_posixtime_modified_list

    TemplateInfo:
        Tsetter_native_column
        tbl = annotmatch
        col = annotmatch_posixtime_modified
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_POSIXTIME_MODIFIED,)
    ibs.db.set(const.ANNOTMATCH_TABLE, colnames, annotmatch_posixtime_modified_list,
               id_iter, duplicate_behavior=duplicate_behavior)


@register_ibs_method
@accessor_decors.setter
def set_annotmatch_reviewed(ibs, annotmatch_rowid_list, annotmatch_reviewed_list, duplicate_behavior='error'):
    r""" annotmatch_reviewed_list -> annotmatch.annotmatch_reviewed[annotmatch_rowid_list]

    Args:
        annotmatch_rowid_list
        annotmatch_reviewed_list

    TemplateInfo:
        Tsetter_native_column
        tbl = annotmatch
        col = annotmatch_reviewed
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_REVIEWED,)
    ibs.db.set(const.ANNOTMATCH_TABLE, colnames, annotmatch_reviewed_list,
               id_iter, duplicate_behavior=duplicate_behavior)


@register_ibs_method
@accessor_decors.setter
def set_annotmatch_reviewer(ibs, annotmatch_rowid_list, annotmatch_reviewer_list, duplicate_behavior='error'):
    r""" annotmatch_reviewer_list -> annotmatch.annotmatch_reviewer[annotmatch_rowid_list]

    Args:
        annotmatch_rowid_list
        annotmatch_reviewer_list

    TemplateInfo:
        Tsetter_native_column
        tbl = annotmatch
        col = annotmatch_reviewer
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_REVIEWER,)
    ibs.db.set(const.ANNOTMATCH_TABLE, colnames, annotmatch_reviewer_list,
               id_iter, duplicate_behavior=duplicate_behavior)


@register_ibs_method
@accessor_decors.setter
def set_annotmatch_tag_text(ibs, annotmatch_rowid_list, annotmatch_tag_text_list, duplicate_behavior='error'):
    r""" annotmatch_tag_text_list -> annotmatch.annotmatch_tag_text[annotmatch_rowid_list]

    Args:
        annotmatch_rowid_list
        annotmatch_tag_text_list

    TemplateInfo:
        Tsetter_native_column
        tbl = annotmatch
        col = annotmatch_tag_text
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_TAG_TEXT,)
    ibs.db.set(const.ANNOTMATCH_TABLE, colnames, annotmatch_tag_text_list,
               id_iter, duplicate_behavior=duplicate_behavior)


@register_ibs_method
@accessor_decors.setter
def set_annotmatch_truth(ibs, annotmatch_rowid_list, annotmatch_truth_list, duplicate_behavior='error'):
    r""" annotmatch_truth_list -> annotmatch.annotmatch_truth[annotmatch_rowid_list]

    Args:
        annotmatch_rowid_list
        annotmatch_truth_list

    TemplateInfo:
        Tsetter_native_column
        tbl = annotmatch
        col = annotmatch_truth
    """
    id_iter = annotmatch_rowid_list
    colnames = (ANNOTMATCH_TRUTH,)
    ibs.db.set(const.ANNOTMATCH_TABLE, colnames, annotmatch_truth_list,
               id_iter, duplicate_behavior=duplicate_behavior)


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ibeis.control._autogen_annotmatch_funcs
        python -m ibeis.control._autogen_annotmatch_funcs --allexamples
    """
    import multiprocessing
    multiprocessing.freeze_support()
    import utool as ut
    ut.doctest_funcs()
