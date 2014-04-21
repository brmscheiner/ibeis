#!/usr/bin/env python
"""
This is a hacky script meant to be run interactively
"""
# TODO: ADD COPYRIGHT TAG
from __future__ import absolute_import, division, print_function
import ibeis
ibeis._preload()
from plottool import draw_func2 as df2
from ibeis.dev import main_helpers
from ibeis import interact
import utool
import multiprocessing
print, print_, printDBG, rrr, profile = utool.inject(__name__, '[dev]', DEBUG=False)


def vdd(ibs=None):
    utool.view_directory(ibs.get_dbpath())


def show_rids(ibs, qrid_list):
    for rid in qrid_list:
        interact.ishow_chjp(ibs, rid, fnum=df2.next_fnum())


def query_rids(ibs, qrid_list):
    qrid2_qres = ibs.query_database(qrid_list)
    for qrid in qrid_list:
        qres = qrid2_qres[qrid]
        interact.ishow_qres(ibs, qres, fnum=df2.next_fnum(), annote_mode=1)
    return qrid2_qres


def sver_rids(ibs, qrid_list):
    qrid2_qres = ibs.query_database(qrid_list)
    for qrid in qrid_list:
        qres = qrid2_qres[qrid]
        rid2 = qres.get_top_rids()[0]
        interact.ishow_sver(ibs, qrid, rid2, fnum=df2.next_fnum(), annote_mode=1)
    return qrid2_qres


def printcfg(ibs):
    ibs.cfg.printme3()
    print(ibs.cfg.query_cfg.get_uid())


#@utool.indent_decor('[dev]')
@profile
def run_experiments(ibs, qrid_list):
    print('\n')
    print('==========================')
    print('RUN INVESTIGATIONS %s' % ibs.get_dbname())
    print('==========================')
    input_test_list = params.args.tests[:]
    print('input_test_list = %r' % (input_test_list,))
    # fnum = 1

    valid_test_list = []  # build list for printing in case of failure

    def intest(*args):
        for testname in args:
            valid_test_list.append(testname)
            ret = testname in input_test_list
            if ret:
                input_test_list.remove(testname)
                print('+===================')
                print('| running testname=%s' % testname)
                return ret
        return False

    if intest('info'):
        print(ibs.get_infostr())
    if intest('printcfg'):
        printcfg(ibs)
    if intest('tables'):
        ibs.print_tables()
    if intest('imgtbl'):
        ibs.print_image_table()
    if intest('query'):
        qrid2_qres = query_rids(ibs, qrid_list)
    if intest('sver'):
        sver_rids(ibs, qrid_list)
    if intest('show'):
        show_rids(ibs, qrid_list)

    # Allow any testcfg to be in tests like:
    # vsone_1 or vsmany_3
    #testcfg_keys = vars(experiment_configs).keys()
    #testcfg_locals = [key for key in testcfg_keys if key.find('_') != 0]
    #for test_cfg_name in testcfg_locals:
        #if intest(test_cfg_name):
            #fnum = experiment_harness.test_configurations(ibs, qrid_list, [test_cfg_name], fnum)

    if intest('help'):
        print('valid tests are:')
        print(''.join(utool.indent_list('\n -t ', valid_test_list)))
        return

    if len(input_test_list) > 0:
        print('valid tests are: \n')
        print('\n'.join(valid_test_list))
        raise Exception('Unknown tests: %r ' % input_test_list)
    return locals()


@profile
def dev_main():
    print('++dev')
    main_locals = ibeis.main(gui='--gui' in sys.argv)
    ibs  = main_locals['ibs']
    back = main_locals['back']

    fnum = 1
    qrid_list = main_helpers.get_test_qrids(ibs)
    expt_locals = run_experiments(ibs, qrid_list)

    if not '--nopresent' in sys.argv:
        df2.present()
    ipy = (not '--gui' in sys.argv) or ('--cmd' in sys.argv)
    main_execstr = ibeis.main_loop(main_locals, ipy=ipy)
    return locals(), main_execstr

if __name__ == '__main__':
    """
        The Developer Script
            A command line interface to almost everything

            -w     # wait / show the gui / figures are visible
            --cmd  # ipython shell to play with variables
            -t     # run list of tests

            Examples:
                ./dev.py -t query -w
    """
    multiprocessing.freeze_support()  # for win32
    from ibeis.dev.all_imports import *  # NOQA
    dev_locals, main_execstr = dev_main()
    dev_execstr = utool.execstr_dict(dev_locals, 'dev_locals')
    execstr = dev_execstr + '\n' + main_execstr
    exec(execstr)
