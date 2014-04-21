from __future__ import absolute_import, division, print_function
import utool
from ibeis import viz
from ibeis.viz import viz_helpers as vh
from . import interact_helpers as ih

(print, print_, printDBG, rrr, profile) = utool.inject(
    __name__, '[interact_sver]', DEBUG=False)


def ishow_sver(ibs, rid1, rid2, chipmatch_FILT=None, rid2_svtup=None, fnum=None, **kwargs):
    fig = ih.begin_interaction('sver', fnum)
    mode_ptr = [2]
    if chipmatch_FILT is None or rid2_svtup is None:
        chipmatch_FILT, rid2_svtup = viz._compute_svvars(ibs, rid1)

    def _sv_view(**kwargs):
        kwargs['show_assign'] = kwargs.get('show_assign', False)
        viz.show_sver(ibs, rid1, rid2, chipmatch_FILT, rid2_svtup, fnum=fnum, **kwargs)

    def _on_sv_click(event):
        print_('[inter] clicked sv')
        ax, x, y = event.inaxes, event.xdata, event.ydata
        if ih.clicked_outside_axis(event):
            print('... out of axis')
            mode_ptr[0] = (mode_ptr[0] + 1) % 3
            kwargs['show_kpts']  = mode_ptr[0] == 2
            kwargs['show_lines'] = mode_ptr[0] >= 1
            _sv_view(**kwargs)
        else:
            viztype = vh.get_ibsdat(ax, 'viztype')
            print_('[ic] viztype=%r' % viztype)
            if viztype in ['homogblend', 'affblend', 'source', 'dest']:
                pass
            else:
                print('...Unknown viztype: %r' % viztype)
        viz.draw()

    _sv_view()
    viz.draw()
    ih.connect_callback(fig, 'button_press_event', _on_sv_click)
