# -*- coding: utf-8 -*-
"""
Dependencies: flask, tornado
"""
from __future__ import absolute_import, division, print_function
from ibeis.control import controller_inject
from ibeis.web import appfuncs as appf
import utool as ut

(print, rrr, profile) = ut.inject2(__name__)

register_route = controller_inject.get_ibeis_flask_route(__name__)


@register_route('/demo/', methods=['GET'], __route_authenticate__=False)
def demo(*args, **kwargs):
    # Return HTML

    embedded = dict(globals(), **locals())
    return appf.template(None, 'demo', **embedded)


if __name__ == '__main__':
    """
    CommandLine:
        python -m ibeis.web.app
        python -m ibeis.web.app --allexamples
        python -m ibeis.web.app --allexamples --noface --nosrc
    """
    import multiprocessing
    multiprocessing.freeze_support()  # for win32
    import utool as ut  # NOQA
    ut.doctest_funcs()
