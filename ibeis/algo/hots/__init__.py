# -*- coding: utf-8 -*-
# Autogenerated on 12:39:11 2016/10/13
# flake8: noqa
from __future__ import absolute_import, division, print_function, unicode_literals
from ibeis.algo.hots import _pipeline_helpers
from ibeis.algo.hots import chip_match
from ibeis.algo.hots import exceptions
from ibeis.algo.graph_iden import graph_iden
from ibeis.algo.hots import hstypes
from ibeis.algo.hots import match_chips4
from ibeis.algo.hots import multi_index
from ibeis.algo.hots import name_scoring
from ibeis.algo.hots import neighbor_index
from ibeis.algo.hots import neighbor_index_cache
from ibeis.algo.hots import nn_weights
from ibeis.algo.hots import old_chip_match
from ibeis.algo.hots import pipeline
from ibeis.algo.hots import query_params
from ibeis.algo.hots import query_request
from ibeis.algo.hots import scoring
from ibeis.algo.hots import vsone_pipeline
import utool
print, rrr, profile = utool.inject2(__name__, '[ibeis.algo.hots]')


def reassign_submodule_attributes(verbose=True):
    """
    why reloading all the modules doesnt do this I don't know
    """
    import sys
    if verbose and '--quiet' not in sys.argv:
        print('dev reimport')
    # Self import
    import ibeis.algo.hots
    # Implicit reassignment.
    seen_ = set([])
    for tup in IMPORT_TUPLES:
        if len(tup) > 2 and tup[2]:
            continue  # dont import package names
        submodname, fromimports = tup[0:2]
        submod = getattr(ibeis.algo.hots, submodname)
        for attr in dir(submod):
            if attr.startswith('_'):
                continue
            if attr in seen_:
                # This just holds off bad behavior
                # but it does mimic normal util_import behavior
                # which is good
                continue
            seen_.add(attr)
            setattr(ibeis.algo.hots, attr, getattr(submod, attr))


def reload_subs(verbose=True):
    """ Reloads ibeis.algo.hots and submodules """
    if verbose:
        print('Reloading submodules')
    rrr(verbose=verbose)
    def wrap_fbrrr(mod):
        def fbrrr(*args, **kwargs):
            """ fallback reload """
            if verbose:
                print('No fallback relaod for mod=%r' % (mod,))
            # Breaks ut.Pref (which should be depricated anyway)
            # import imp
            # imp.reload(mod)
        return fbrrr
    def get_rrr(mod):
        if hasattr(mod, 'rrr'):
            return mod.rrr
        else:
            return wrap_fbrrr(mod)
    def get_reload_subs(mod):
        return getattr(mod, 'reload_subs', wrap_fbrrr(mod))
    get_rrr(_pipeline_helpers)(verbose=verbose)
    get_rrr(chip_match)(verbose=verbose)
    get_rrr(exceptions)(verbose=verbose)
    get_rrr(graph_iden)(verbose=verbose)
    get_rrr(hstypes)(verbose=verbose)
    get_rrr(match_chips4)(verbose=verbose)
    get_rrr(multi_index)(verbose=verbose)
    get_rrr(name_scoring)(verbose=verbose)
    get_rrr(neighbor_index)(verbose=verbose)
    get_rrr(neighbor_index_cache)(verbose=verbose)
    get_rrr(nn_weights)(verbose=verbose)
    get_rrr(old_chip_match)(verbose=verbose)
    get_rrr(pipeline)(verbose=verbose)
    get_rrr(query_params)(verbose=verbose)
    get_rrr(query_request)(verbose=verbose)
    get_rrr(scoring)(verbose=verbose)
    get_rrr(vsone_pipeline)(verbose=verbose)
    rrr(verbose=verbose)
    try:
        # hackish way of propogating up the new reloaded submodule attributes
        reassign_submodule_attributes(verbose=verbose)
    except Exception as ex:
        print(ex)
rrrr = reload_subs

IMPORT_TUPLES = [
    ('_pipeline_helpers', None),
    ('chip_match', None),
    ('exceptions', None),
    ('graph_iden', None),
    ('hstypes', None),
    ('match_chips4', None),
    ('multi_index', None),
    ('name_scoring', None),
    ('neighbor_index', None),
    ('neighbor_index_cache', None),
    ('nn_weights', None),
    ('old_chip_match', None),
    ('pipeline', None),
    ('query_params', None),
    ('query_request', None),
    ('scoring', None),
    ('vsone_pipeline', None),
]
"""
Regen Command:
    cd /home/joncrall/code/ibeis/ibeis/algo/hots
    makeinit.py --modname=ibeis.algo.hots
"""
