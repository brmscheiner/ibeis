# Dependencies: flask, tornado
from __future__ import absolute_import, division, print_function
# HTTP / HTML
import tornado.wsgi
import tornado.httpserver
import flask
from flask import request, redirect, url_for
import optparse
import logging
import socket
import simplejson as json
# IBEIS
import ibeis
from ibeis.control.SQLDatabaseControl import (SQLDatabaseController,  # NOQA
                                              SQLAtomicContext)
from ibeis.control import _sql_helpers
from ibeis.constants import KEY_DEFAULTS, SPECIES_KEY
import utool
import utool as ut
# Web Internal
from ibeis.web import appfuncs, navbar, DBWEB_SCHEMA
# Others
from datetime import date
from os.path import join


BROWSER = ut.get_argflag('--browser')
DEFAULT_PORT = 5000
app = flask.Flask(__name__)
global_args = {
    'NAVBAR': navbar.NavbarClass(),
    'YEAR':   date.today().year,
}


################################################################################


@app.route('/')
@app.route('/<filename>.html')
def root(filename=''):
    return template('', filename)


@app.route('/turk')
@app.route('/turk/<filename>.html')
def turk(filename=''):
    if 'refer' in request.args.keys():
        refer = request.args['refer']
    else:
        refer = None

    if filename == 'detection':
        if 'gid' in request.args.keys():
            gid = int(request.args['gid'])
        else:
            with SQLAtomicContext(app.db):
                gid = appfuncs.get_next_detection_turk_candidate(app)
        finished = gid is None
        if not finished:
            gpath = app.ibeis.get_image_paths(gid)
            image = appfuncs.open_oriented_image(gpath)
            image_src = appfuncs.embed_image_html(image, filter_width=False)
            # Get annotations
            width, height = app.ibeis.get_image_sizes(gid)
            scale_factor = 700.0 / float(width)
            aid_list = app.ibeis.get_image_aids(gid)
            annot_bbox_list = app.ibeis.get_annot_bboxes(aid_list)
            annot_thetas_list = app.ibeis.get_annot_thetas(aid_list)
            species_list = app.ibeis.get_annot_species(aid_list)
            # Get annotation bounding boxes
            annotation_list = []
            for annot_bbox, annot_theta, species in zip(annot_bbox_list, annot_thetas_list, species_list):
                temp = {}
                temp['left']   = int(scale_factor * annot_bbox[0])
                temp['top']    = int(scale_factor * annot_bbox[1])
                temp['width']  = int(scale_factor * (annot_bbox[2]))
                temp['height'] = int(scale_factor * (annot_bbox[3]))
                temp['label']  = species
                temp['angle']  = float(annot_theta)
                annotation_list.append(temp)
            if len(species_list) > 0:
              species = max(set(species_list), key=species_list.count)  # Get most common species
            else:
              species = KEY_DEFAULTS[SPECIES_KEY]
        else:
            gpath = None
            image_src = None
            species = None
            annotation_list = []
          
        if refer is not None and 'refer_aid' in request.args.keys():
            refer_aid = request.args['refer_aid']
        else:
            refer_aid = None
        return template('turk', filename,
                        gid=gid,
                        species=species,
                        image_path=gpath,
                        image_src=image_src,
                        finished=finished,
                        annotation_list=annotation_list,
                        refer=refer,
                        refer_aid=refer_aid)
    elif filename == 'viewpoint':
        if 'aid' in request.args.keys():
            aid = int(request.args['aid'])
        else:
            with SQLAtomicContext(app.db):
                aid = appfuncs.get_next_viewpoint_turk_candidate(app)
        finished = aid is None
        if not finished:
            gid       = app.ibeis.get_annot_gids(aid)
            gpath     = app.ibeis.get_annot_chip_paths(aid)
            image     = appfuncs.open_oriented_image(gpath)
            image_src = appfuncs.embed_image_html(image)
        else:
            gid       = None
            gpath     = None
            image_src = None
        print("VIEW:", aid, gid)
        return template('turk', filename,
                        aid=aid,
                        gid=gid,
                        image_path=gpath,
                        image_src=image_src,
                        finished=finished,
                        refer=refer)
    elif filename == 'viewpoint-commit':
        # Things that need to be committed
        where_clause = "viewpoint_value_avg>=?"
        viewpoint_rowid_list = appfuncs.get_viewpoint_rowids_where(app, where_clause=where_clause, params=[0.0])
        aid_list = appfuncs.get_viewpoint_aid(app, viewpoint_rowid_list)
        viewpoint_list = appfuncs.get_viewpoint_values_from_aids(app, aid_list, 'viewpoint_value_avg')
        app.ibeis.set_annot_viewpoint(aid_list, viewpoint_list, convert_radians=True)
        count = len(aid_list)
        # Flagged aids
        where_clause = "viewpoint_value_2!=? AND viewpoint_value_avg=?"
        viewpoint_rowid_list = appfuncs.get_viewpoint_rowids_where(app, where_clause=where_clause, params=[-1.0, -1.0])
        flagged_aid_list = appfuncs.get_viewpoint_aid(app, viewpoint_rowid_list)
        # Skipped aids
        where_clause = "viewpoint_value_2!=? AND viewpoint_value_avg=?"
        viewpoint_rowid_list = appfuncs.get_viewpoint_rowids_where(app, where_clause=where_clause, params=[-1.0, -2.0])
        skipped_aid_list = appfuncs.get_viewpoint_aid(app, viewpoint_rowid_list)
        # Return output
        return "Commiting %d viewpoints to the database...<br/>Flagged: %r<br/>Skipped: %r" % (count, flagged_aid_list, skipped_aid_list)
    else:
        return template('turk', filename)


@app.route('/submit/viewpoint.html', methods=['POST'])
def submit_viewpoint():
    aid = int(request.form['viewpoint-aid'])
    value = int(request.form['viewpoint-value'])
    if request.form['viewpoint-submit'].lower() == 'skip':
        value = -2
    # Get current values
    value_1 = appfuncs.get_viewpoint_values_from_aids(app, [aid], 'viewpoint_value_1')[0]
    value_2 = appfuncs.get_viewpoint_values_from_aids(app, [aid], 'viewpoint_value_2')[0]
    if value_1 is None:
        appfuncs.set_viewpoint_values_from_aids(app, [aid], [value], 'viewpoint_value_1')
        value_1 = value
    elif value_2 is None:
        appfuncs.set_viewpoint_values_from_aids(app, [aid], [value], 'viewpoint_value_2')
        value_2 = value
        if value_1 >= 0 and value_2 >= 0:
            # perform check against two viewpoint annotations
            if abs(value_1 - value_2) <= 45:
                value = (value_1 + value_2) / 2
                appfuncs.set_viewpoint_values_from_aids(app, [aid], [value], 'viewpoint_value_avg')
            else:
                # We don't need to do anything here, viewpoints are promoted out of the error state (default) if consistent
                print('[web] FLAGGED - VIEWPOINTS INCONSISTENT')
        else:
            print('[web] SKIPPED - VIEWPOINTS UNSURE')
            appfuncs.set_viewpoint_values_from_aids(app, [aid], [-2], 'viewpoint_value_avg')
    else:
        print('[web] SKIPPED - TOO MANY VIEWPOINTS')
    print("[web] aid: %d, value: %d | %s %s" % (aid, value, value_1, value_2))
    # Return HTML
    return redirect(url_for('turk', filename='viewpoint'))


@app.route('/submit/detection.html', methods=['POST'])
def submit_detection():
    gid = int(request.form['detection-gid'])
    count = 1
    if request.form['detection-submit'].lower() == 'skip':
        count = -1
    appfuncs.set_review_count_from_gids(app, [gid], [count])
    if count == 1:
        width, height = app.ibeis.get_image_sizes(gid)
        scale_factor = float(width) / 700.0
        # Get aids
        aid_list = app.ibeis.get_image_aids(gid)
        app.ibeis.delete_annots(aid_list)
        annotation_list = json.loads(request.form['detection-annotations'])
        bbox_list = [
            (
                int(scale_factor * annot['left']),
                int(scale_factor * annot['top']),
                int(scale_factor * annot['width']),
                int(scale_factor * annot['height']),
            )
            for annot in annotation_list
        ]
        theta_list = [
            float(annot['angle'])
            for annot in annotation_list
        ]
        species_list = [
            annot['label']
            for annot in annotation_list
        ]
        print("[web] gid: %d, bbox_list: %r, species_list: %r" % (gid, annotation_list, species_list))
        aid_list_new = app.ibeis.add_annots([gid] * len(annotation_list), bbox_list, theta_list=theta_list, species_list=species_list)
        appfuncs.replace_aids(app, aid_list, aid_list_new)
    if 'refer' in request.args.keys() and request.args['refer'] == 'viewpoint':
        return redirect(url_for('turk', filename='viewpoint'))
    else:
        return redirect(url_for('turk', filename='detection'))


@app.route('/api')
@app.route('/api/<function>.json', methods=['GET', 'POST'])
def api(function=None):
    template = {
        'status': {
            'success': False,
            'code': '',
        },
    }
    print('Function:', function)
    print('POST:', dict(request.form))
    print('GET:',  dict(request.args))
    if function is None:
        template['status']['success'] = True
        template['status']['code'] = 'USAGE: /api/[ibeis_function_name].json'
    else:
        function = function.lower()
        if appfuncs.check_valid_function_name(function):
            function = 'app.ibeis.%s' % function
            exists = True
            try:
                func = eval(function)
                ret = func()
            except AttributeError:
                exists = False
            if exists:
                template['status']['success'] = True
                template['function'] = function
                template['return'] = ret
            else:
                template['status']['success'] = False
                template['status']['code'] = 'ERROR: Specified IBEIS function not visible or implemented'
        else:
            template['status']['success'] = False
            template['status']['code'] = 'ERROR: Specified IBEIS function not valid Python function'
    return json.dumps(template)


################################################################################


def template(template_directory='', template_filename='', **kwargs):
    if len(template_filename) == 0:
        template_filename = 'index'
    template_ = join(template_directory, template_filename + '.html')
    # Update global args with the template's args
    _global_args = dict(global_args)
    _global_args.update(kwargs)
    print(template_)
    return flask.render_template(template_, **_global_args)


################################################################################


def init_database(app, reset_db):
    database_dir = utool.get_app_resource_dir('ibeis', 'web')
    database_filename = 'app.sqlite3'
    database_filepath = join(database_dir, database_filename)
    utool.ensuredir(database_dir)
    if reset_db:
        utool.remove_file(database_filepath)
    app.dbweb_version_expected = '1.0.0'
    app.db = SQLDatabaseController(database_dir, database_filename)
    _sql_helpers.ensure_correct_version(
        app.ibeis,
        app.db,
        app.dbweb_version_expected,
        DBWEB_SCHEMA
    )


def start_tornado(app, port=5000, browser=BROWSER, blocking=False, reset_db=True, database_init=None):
    def _start_tornado():
        http_server = tornado.httpserver.HTTPServer(
            tornado.wsgi.WSGIContainer(app))
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    # Open the web internal database
    init_database(app, reset_db=reset_db)
    # Initialize the web server
    logging.getLogger().setLevel(logging.INFO)
    try:
        server_ip_address = socket.gethostbyname(socket.gethostname())
    except:
        server_ip_address = '127.0.0.1'
    url = 'http://%s:%s' % (server_ip_address, port)
    print('[web] Tornado server starting at %s' % (url,))
    if browser:
        import webbrowser
        webbrowser.open(url)
    if database_init is not None:
        database_init(app)
    # Blocking
    _start_tornado()
    # if blocking:
    #     _start_tornado()
    # else:
    #     import threading
    #     threading.Thread(target=_start_tornado).start()


def start_from_terminal():
    '''
    Parse command line options and start the server.
    '''
    parser = optparse.OptionParser()
    parser.add_option(
        '-p', '--port',
        help='which port to serve content on',
        type='int', default=DEFAULT_PORT)
    parser.add_option(
        '--db',
        help='specify an IBEIS database',
        type='str', default='testdb0')

    opts, args = parser.parse_args()
    app.ibeis = ibeis.opendb(db=opts.db)
    start_tornado(app, opts.port, database_init=appfuncs.database_init)


def start_from_ibeis(ibeis, port=DEFAULT_PORT):
    '''
    Parse command line options and start the server.
    '''
    app.ibeis = ibeis
    start_tornado(app, port, database_init=appfuncs.database_init)


if __name__ == '__main__':
    start_from_terminal()
