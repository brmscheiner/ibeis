# Dependencies: flask, tornado
from __future__ import absolute_import, division, print_function
# HTTP / HTML
import tornado.wsgi
import tornado.httpserver
import flask
from flask import request, redirect, url_for, make_response
import optparse
import logging
import socket
import simplejson as json
# IBEIS
import ibeis
from ibeis.control.SQLDatabaseControl import (SQLDatabaseController,  # NOQA
                                              SQLAtomicContext)
from ibeis.constants import KEY_DEFAULTS, SPECIES_KEY, Species
import utool as ut
# Web Internal
from ibeis.web import appfuncs as ap
# Others
import traceback
import ibeis.constants as const
import random
import math


BROWSER = ut.get_argflag('--browser')
DEFAULT_PORT = 5000
PAGE_SIZE = 500
app = flask.Flask(__name__)


################################################################################


def encounter_image_processed(gid_list):
    images_reviewed = [ reviewed == 1 for reviewed in app.ibs.get_image_reviewed(gid_list) ]
    return images_reviewed


def encounter_annot_viewpoint_processed(aid_list):
    annots_reviewed = [ reviewed is not None for reviewed in app.ibs.get_annot_yaws(aid_list) ]
    return annots_reviewed


def encounter_annot_quality_processed(aid_list):
    annots_reviewed = [ reviewed is not None and reviewed is not -1 for reviewed in app.ibs.get_annot_qualities(aid_list) ]
    return annots_reviewed


def encounter_annot_additional_processed(aid_list, nid_list):
    sex_list = app.ibs.get_annot_sex(aid_list)
    age_list = app.ibs.get_annot_age_months_est(aid_list)
    annots_reviewed = [
        (nid < 0) or (nid > 0 and sex >= 0 and -1 not in list(age) and list(age).count(None) < 2)
        for nid, sex, age in zip(nid_list, sex_list, age_list)
    ]
    return annots_reviewed


def convert_old_viewpoint_to_yaw(view_angle):
    ''' we initially had viewpoint coordinates inverted

    Example:
        >>> import math
        >>> TAU = 2 * math.pi
        >>> old_viewpoint_labels = [
        >>>     ('left'       ,   0, 0.000 * TAU,),
        >>>     ('frontleft'  ,  45, 0.125 * TAU,),
        >>>     ('front'      ,  90, 0.250 * TAU,),
        >>>     ('frontright' , 135, 0.375 * TAU,),
        >>>     ('right'      , 180, 0.500 * TAU,),
        >>>     ('backright'  , 225, 0.625 * TAU,),
        >>>     ('back'       , 270, 0.750 * TAU,),
        >>>     ('backleft'   , 315, 0.875 * TAU,),
        >>> ]
        >>> fmtstr = 'old %15r %.2f -> new %15r %.2f'
        >>> for lbl, angle, radians in old_viewpoint_labels:
        >>>     print(fmtstr % (lbl, angle, lbl, convert_old_viewpoint_to_yaw(angle)))
    '''
    if view_angle is None:
        return None
    view_angle = ut.deg_to_rad(view_angle)
    yaw = (-view_angle + (const.TAU / 2)) % const.TAU
    return yaw


def convert_yaw_to_old_viewpoint(yaw):
    ''' we initially had viewpoint coordinates inverted

    Example:
        >>> import math
        >>> TAU = 2 * math.pi
        >>> old_viewpoint_labels = [
        >>>     ('left'       ,   0, 0.000 * TAU,),
        >>>     ('frontleft'  ,  45, 0.125 * TAU,),
        >>>     ('front'      ,  90, 0.250 * TAU,),
        >>>     ('frontright' , 135, 0.375 * TAU,),
        >>>     ('right'      , 180, 0.500 * TAU,),
        >>>     ('backright'  , 225, 0.625 * TAU,),
        >>>     ('back'       , 270, 0.750 * TAU,),
        >>>     ('backleft'   , 315, 0.875 * TAU,),
        >>> ]
        >>> fmtstr = 'original_angle %15r %.2f -> yaw %15r %.2f -> reconstructed_angle %15r %.2f'
        >>> for lbl, angle, radians in old_viewpoint_labels:
        >>>     yaw = convert_old_viewpoint_to_yaw(angle)
        >>>     reconstructed_angle = convert_yaw_to_old_viewpoint(yaw)
        >>>     print(fmtstr % (lbl, angle, lbl, yaw, lbl, reconstructed_angle))
    '''
    if yaw is None:
        return None
    view_angle = ((const.TAU / 2) - yaw) % const.TAU
    view_angle = ut.rad_to_deg(view_angle)
    return view_angle


################################################################################


# @app.after_request
# def add_header(response):
#     response.headers['Cache-Control'] = 'public, max-age=%d' % (60 * 60 * 24, )
#     return response


@app.route('/')
def root():
    return ap.template(None)


@app.route('/view')
def view():
    aid_list = app.ibs.filter_aids_count()
    gid_list = app.ibs.get_annot_gids(aid_list)
    nid_list = app.ibs.get_annot_name_rowids(aid_list)
    unixtime_list = app.ibs.get_image_unixtime(gid_list)
    datetime_list = [
        ut.unixtime_to_datetime(unixtime)
        if unixtime is not None else
        'UNKNOWN'
        for unixtime in unixtime_list
    ]
    datetime_split_list = [ datetime.split(' ') for datetime in datetime_list ]
    date_list = [ datetime_split[0] if len(datetime_split) == 2 else 'UNKNOWN' for datetime_split in datetime_split_list ]

    value = 0
    label_list = []
    value_list = []
    index_list = []
    seen_set = set()
    previous_seen_set = set()
    current_seen_set = set()
    last_date = None
    date_seen_dict = {}
    for index, (aid, nid, date) in enumerate(zip(aid_list, nid_list, date_list)):
        if date not in date_seen_dict:
            date_seen_dict[date] = [0, 0, 0]
        date_seen_dict[date][0] += 1
        index_list.append(index)
        if nid not in seen_set:
            value += 1
            seen_set.add(nid)
            current_seen_set.add(nid)
            date_seen_dict[date][1] += 1
        if nid not in previous_seen_set:
            date_seen_dict[date][2] += 1
        value_list.append(value)
        if date != last_date and date != 'UNKNOWN':
            last_date = date
            previous_seen_set = set(current_seen_set)
            current_seen_set = set()
            label_list.append(date)
        else:
            label_list.append('')

    date_seen_dict.pop('UNKNOWN', None)
    bar_label_list = sorted(date_seen_dict.keys())
    bar_value_list1 = [ date_seen_dict[date][0] for date in bar_label_list ]
    bar_value_list2 = [ date_seen_dict[date][1] for date in bar_label_list ]
    bar_value_list3 = [ date_seen_dict[date][2] for date in bar_label_list ]

    # Counts
    eid_list = app.ibs.get_valid_eids()
    gid_list = app.ibs.get_valid_gids()
    aid_list = app.ibs.get_valid_aids()
    nid_list = app.ibs.get_valid_nids()

    return ap.template('view',
                       line_index_list=index_list,
                       line_label_list=label_list,
                       line_value_list=value_list,
                       bar_label_list=bar_label_list,
                       bar_value_list1=bar_value_list1,
                       bar_value_list2=bar_value_list2,
                       bar_value_list3=bar_value_list3,
                       eid_list=eid_list,
                       eid_list_str=','.join(map(str, eid_list)),
                       num_eids=len(eid_list),
                       gid_list=gid_list,
                       gid_list_str=','.join(map(str, gid_list)),
                       num_gids=len(gid_list),
                       aid_list=aid_list,
                       aid_list_str=','.join(map(str, aid_list)),
                       num_aids=len(aid_list),
                       nid_list=nid_list,
                       nid_list_str=','.join(map(str, nid_list)),
                       num_nids=len(nid_list))


@app.route('/view/encounters')
def view_encounters():
    try:
        filtered = True
        eid = request.args.get('eid', '')
        if len(eid) > 0:
            eid_list = eid.strip().split(',')
            eid_list = [ None if eid_ == 'None' or eid_ == '' else int(eid_) for eid_ in eid_list ]
        else:
            eid_list = app.ibs.get_valid_eids()
            filtered = False
        start_time_posix_list = app.ibs.get_encounter_start_time_posix(eid_list)
        datetime_list = [
            ut.unixtime_to_datetime(start_time_posix)
            if start_time_posix is not None else
            'Unknown'
            for start_time_posix in start_time_posix_list
        ]
        gids_list = [ app.ibs.get_valid_gids(eid=eid_) for eid_ in eid_list ]
        aids_list = [ ut.flatten(app.ibs.get_image_aids(gid_list)) for gid_list in gids_list ]
        images_reviewed_list           = [ encounter_image_processed(gid_list) for gid_list in gids_list ]
        annots_reviewed_viewpoint_list = [ encounter_annot_viewpoint_processed(aid_list) for aid_list in aids_list ]
        annots_reviewed_quality_list   = [ encounter_annot_quality_processed(aid_list) for aid_list in aids_list ]
        image_processed_list           = [ images_reviewed.count(True) for images_reviewed in images_reviewed_list ]
        annot_processed_viewpoint_list = [ annots_reviewed.count(True) for annots_reviewed in annots_reviewed_viewpoint_list ]
        annot_processed_quality_list   = [ annots_reviewed.count(True) for annots_reviewed in annots_reviewed_quality_list ]
        reviewed_list = [ all(images_reviewed) and all(annots_reviewed_viewpoint) and all(annot_processed_quality) for images_reviewed, annots_reviewed_viewpoint, annot_processed_quality in zip(images_reviewed_list, annots_reviewed_viewpoint_list, annots_reviewed_quality_list) ]
        encounter_list = zip(
            eid_list,
            app.ibs.get_encounter_text(eid_list),
            app.ibs.get_encounter_num_gids(eid_list),
            image_processed_list,
            app.ibs.get_encounter_num_aids(eid_list),
            annot_processed_viewpoint_list,
            annot_processed_quality_list,
            start_time_posix_list,
            datetime_list,
            reviewed_list,
        )
        encounter_list.sort(key=lambda t: t[7])
        return ap.template('view', 'encounters',
                           filtered=filtered,
                           eid_list=eid_list,
                           eid_list_str=','.join(map(str, eid_list)),
                           num_eids=len(eid_list),
                           encounter_list=encounter_list,
                           num_encounters=len(encounter_list))
    except Exception as e:
        return error404(e)


@app.route('/view/images')
def view_images():
    try:
        filtered = True
        eid_list = []
        gid = request.args.get('gid', '')
        eid = request.args.get('eid', '')
        page = max(0, int(request.args.get('page', 1)))
        if len(gid) > 0:
            gid_list = gid.strip().split(',')
            gid_list = [ None if gid_ == 'None' or gid_ == '' else int(gid_) for gid_ in gid_list ]
        elif len(eid) > 0:
            eid_list = eid.strip().split(',')
            eid_list = [ None if eid_ == 'None' or eid_ == '' else int(eid_) for eid_ in eid_list ]
            gid_list = ut.flatten([ app.ibs.get_valid_gids(eid=eid) for eid_ in eid_list ])
        else:
            gid_list = app.ibs.get_valid_gids()
            filtered = False
        # Page
        page_start = min(len(gid_list), (page - 1) * PAGE_SIZE)
        page_end   = min(len(gid_list), page * PAGE_SIZE)
        page_total = int(math.ceil(len(gid_list) / PAGE_SIZE))
        page_previous = None if page_start == 0 else page - 1
        page_next = None if page_end == len(gid_list) else page + 1
        gid_list = gid_list[page_start:page_end]
        print('[web] Loading Page [ %d -> %d ] (%d), Prev: %s, Next: %s' % (page_start, page_end, len(gid_list), page_previous, page_next, ))
        image_unixtime_list = app.ibs.get_image_unixtime(gid_list)
        datetime_list = [
            ut.unixtime_to_datetime(image_unixtime)
            if image_unixtime is not None
            else
            'Unknown'
            for image_unixtime in image_unixtime_list
        ]
        image_list = zip(
            gid_list,
            [ ','.join(map(str, eid_list_)) for eid_list_ in app.ibs.get_image_eids(gid_list) ],
            app.ibs.get_image_gnames(gid_list),
            image_unixtime_list,
            datetime_list,
            app.ibs.get_image_gps(gid_list),
            app.ibs.get_image_party_tag(gid_list),
            app.ibs.get_image_contributor_tag(gid_list),
            app.ibs.get_image_notes(gid_list),
            encounter_image_processed(gid_list),
        )
        image_list.sort(key=lambda t: t[3])
        return ap.template('view', 'images',
                           filtered=filtered,
                           eid_list=eid_list,
                           eid_list_str=','.join(map(str, eid_list)),
                           num_eids=len(eid_list),
                           gid_list=gid_list,
                           gid_list_str=','.join(map(str, gid_list)),
                           num_gids=len(gid_list),
                           image_list=image_list,
                           num_images=len(image_list),
                           page=page,
                           page_start=page_start,
                           page_end=page_end,
                           page_total=page_total,
                           page_previous=page_previous,
                           page_next=page_next)
    except Exception as e:
        return error404(e)


@app.route('/view/annotations')
def view_annotations():
    try:
        filtered = True
        eid_list = []
        gid_list = []
        aid = request.args.get('aid', '')
        gid = request.args.get('gid', '')
        eid = request.args.get('eid', '')
        page = max(0, int(request.args.get('page', 1)))
        if len(aid) > 0:
            aid_list = aid.strip().split(',')
            aid_list = [ None if aid_ == 'None' or aid_ == '' else int(aid_) for aid_ in aid_list ]
        elif len(gid) > 0:
            gid_list = gid.strip().split(',')
            gid_list = [ None if gid_ == 'None' or gid_ == '' else int(gid_) for gid_ in gid_list ]
            aid_list = ut.flatten(app.ibs.get_image_aids(gid_list))
        elif len(eid) > 0:
            eid_list = eid.strip().split(',')
            eid_list = [ None if eid_ == 'None' or eid_ == '' else int(eid_) for eid_ in eid_list ]
            gid_list = ut.flatten([ app.ibs.get_valid_gids(eid=eid_) for eid_ in eid_list ])
            aid_list = ut.flatten(app.ibs.get_image_aids(gid_list))
        else:
            aid_list = app.ibs.get_valid_aids()
            filtered = False
        # Page
        page_start = min(len(aid_list), (page - 1) * PAGE_SIZE)
        page_end   = min(len(aid_list), page * PAGE_SIZE)
        page_total = int(math.ceil(len(aid_list) / PAGE_SIZE))
        page_previous = None if page_start == 0 else page - 1
        page_next = None if page_end == len(aid_list) else page + 1
        aid_list = aid_list[page_start:page_end]
        print('[web] Loading Page [ %d -> %d ] (%d), Prev: %s, Next: %s' % (page_start, page_end, len(aid_list), page_previous, page_next, ))
        annotation_list = zip(
            aid_list,
            app.ibs.get_annot_gids(aid_list),
            [ ','.join(map(str, eid_list_)) for eid_list_ in app.ibs.get_annot_eids(aid_list) ],
            app.ibs.get_annot_image_names(aid_list),
            app.ibs.get_annot_names(aid_list),
            app.ibs.get_annot_exemplar_flags(aid_list),
            app.ibs.get_annot_species_texts(aid_list),
            app.ibs.get_annot_yaw_texts(aid_list),
            app.ibs.get_annot_quality_texts(aid_list),
            app.ibs.get_annot_sex_texts(aid_list),
            app.ibs.get_annot_age_months_est(aid_list),
            [ reviewed_viewpoint and reviewed_quality for reviewed_viewpoint, reviewed_quality in zip(encounter_annot_viewpoint_processed(aid_list), encounter_annot_quality_processed(aid_list)) ],
        )
        annotation_list.sort(key=lambda t: t[0])
        return ap.template('view', 'annotations',
                           filtered=filtered,
                           eid_list=eid_list,
                           eid_list_str=','.join(map(str, eid_list)),
                           num_eids=len(eid_list),
                           gid_list=gid_list,
                           gid_list_str=','.join(map(str, gid_list)),
                           num_gids=len(gid_list),
                           aid_list=aid_list,
                           aid_list_str=','.join(map(str, aid_list)),
                           num_aids=len(aid_list),
                           annotation_list=annotation_list,
                           num_annotations=len(annotation_list),
                           page=page,
                           page_start=page_start,
                           page_end=page_end,
                           page_total=page_total,
                           page_previous=page_previous,
                           page_next=page_next)
    except Exception as e:
        return error404(e)


@app.route('/view/names')
def view_names():
    try:
        filtered = True
        aid_list = []
        eid_list = []
        gid_list = []
        nid = request.args.get('nid', '')
        aid = request.args.get('aid', '')
        gid = request.args.get('gid', '')
        eid = request.args.get('eid', '')
        page = max(0, int(request.args.get('page', 1)))
        if len(nid) > 0:
            nid_list = nid.strip().split(',')
            nid_list = [ None if nid_ == 'None' or nid_ == '' else int(nid_) for nid_ in nid_list ]
        if len(aid) > 0:
            aid_list = aid.strip().split(',')
            aid_list = [ None if aid_ == 'None' or aid_ == '' else int(aid_) for aid_ in aid_list ]
            nid_list = app.ibs.get_annot_name_rowids(aid_list)
        elif len(gid) > 0:
            gid_list = gid.strip().split(',')
            gid_list = [ None if gid_ == 'None' or gid_ == '' else int(gid_) for gid_ in gid_list ]
            aid_list = ut.flatten(app.ibs.get_image_aids(gid_list))
            nid_list = app.ibs.get_annot_name_rowids(aid_list)
        elif len(eid) > 0:
            eid_list = eid.strip().split(',')
            eid_list = [ None if eid_ == 'None' or eid_ == '' else int(eid_) for eid_ in eid_list ]
            gid_list = ut.flatten([ app.ibs.get_valid_gids(eid=eid_) for eid_ in eid_list ])
            aid_list = ut.flatten(app.ibs.get_image_aids(gid_list))
            nid_list = app.ibs.get_annot_name_rowids(aid_list)
        else:
            nid_list = app.ibs.get_valid_nids()
            filtered = False
        # Page
        PAGE_SIZE_ = int(PAGE_SIZE / 5)
        page_start = min(len(nid_list), (page - 1) * PAGE_SIZE_)
        page_end   = min(len(nid_list), page * PAGE_SIZE_)
        page_total = int(math.ceil(len(nid_list) / PAGE_SIZE_))
        page_previous = None if page_start == 0 else page - 1
        page_next = None if page_end == len(nid_list) else page + 1
        nid_list = nid_list[page_start:page_end]
        print('[web] Loading Page [ %d -> %d ] (%d), Prev: %s, Next: %s' % (page_start, page_end, len(nid_list), page_previous, page_next, ))
        aids_list = app.ibs.get_name_aids(nid_list)
        annotations_list = [ zip(
            aid_list_,
            app.ibs.get_annot_gids(aid_list_),
            [ ','.join(map(str, eid_list_)) for eid_list_ in app.ibs.get_annot_eids(aid_list_) ],
            app.ibs.get_annot_image_names(aid_list_),
            app.ibs.get_annot_names(aid_list_),
            app.ibs.get_annot_exemplar_flags(aid_list_),
            app.ibs.get_annot_species_texts(aid_list_),
            app.ibs.get_annot_yaw_texts(aid_list_),
            app.ibs.get_annot_quality_texts(aid_list_),
            app.ibs.get_annot_sex_texts(aid_list_),
            app.ibs.get_annot_age_months_est(aid_list_),
            [ reviewed_viewpoint and reviewed_quality for reviewed_viewpoint, reviewed_quality in zip(encounter_annot_viewpoint_processed(aid_list_), encounter_annot_quality_processed(aid_list_)) ],
        ) for aid_list_ in aids_list ]
        print(len(annotations_list), len(annotations_list[0]), len(annotations_list[1]), len(annotations_list[2]), len(nid_list))
        name_list = zip(
            nid_list,
            annotations_list
        )
        name_list.sort(key=lambda t: t[0])
        return ap.template('view', 'names',
                           filtered=filtered,
                           eid_list=eid_list,
                           eid_list_str=','.join(map(str, eid_list)),
                           num_eids=len(eid_list),
                           gid_list=gid_list,
                           gid_list_str=','.join(map(str, gid_list)),
                           num_gids=len(gid_list),
                           aid_list=aid_list,
                           aid_list_str=','.join(map(str, aid_list)),
                           num_aids=len(aid_list),
                           nid_list=nid_list,
                           nid_list_str=','.join(map(str, nid_list)),
                           num_nids=len(nid_list),
                           name_list=name_list,
                           num_names=len(name_list),
                           page=page,
                           page_start=page_start,
                           page_end=page_end,
                           page_total=page_total,
                           page_previous=page_previous,
                           page_next=page_next)
    except Exception as e:
        return error404(e)


@app.route('/turk')
def turk():
    try:
        eid = request.args.get('eid', '')
        eid = None if eid == 'None' or eid == '' else int(eid)
        return ap.template('turk', None, eid=eid)
    except Exception as e:
        return error404(e)


@app.route('/turk/detection')
def turk_detection():
    try:
        refer_aid = request.args.get('refer_aid', None)
        eid = request.args.get('eid', '')
        eid = None if eid == 'None' or eid == '' else int(eid)

        gid_list = app.ibs.get_valid_gids(eid=eid)
        reviewed_list = encounter_image_processed(gid_list)
        progress = '%0.2f' % (100.0 * reviewed_list.count(True) / len(gid_list), )

        enctext = None if eid is None else app.ibs.get_encounter_text(eid)
        gid = request.args.get('gid', '')
        if len(gid) > 0:
            gid = int(gid)
        else:
            gid_list_ = ut.filterfalse_items(gid_list, reviewed_list)
            if len(gid_list_) == 0:
                gid = None
            else:
                # gid = gid_list_[0]
                gid = random.choice(gid_list_)
        previous = request.args.get('previous', None)
        finished = gid is None
        review = 'review' in request.args.keys()
        display_instructions = request.cookies.get('detection_instructions_seen', 0) == 0
        display_species_examples = False  # request.cookies.get('detection_example_species_seen', 0) == 0
        if not finished:
            gpath = app.ibs.get_image_thumbpath(gid, ensure_paths=True, draw_annots=False)
            image = ap.open_oriented_image(gpath)
            image_src = ap.embed_image_html(image, filter_width=False)
            # Get annotations
            width, height = app.ibs.get_image_sizes(gid)
            scale_factor = 700.0 / float(width)
            aid_list = app.ibs.get_image_aids(gid)
            annot_bbox_list = app.ibs.get_annot_bboxes(aid_list)
            annot_thetas_list = app.ibs.get_annot_thetas(aid_list)
            species_list = app.ibs.get_annot_species_texts(aid_list)
            # Get annotation bounding boxes
            annotation_list = []
            for aid, annot_bbox, annot_theta, species in zip(aid_list, annot_bbox_list, annot_thetas_list, species_list):
                temp = {}
                temp['left']   = int(scale_factor * annot_bbox[0])
                temp['top']    = int(scale_factor * annot_bbox[1])
                temp['width']  = int(scale_factor * (annot_bbox[2]))
                temp['height'] = int(scale_factor * (annot_bbox[3]))
                temp['label']  = species
                temp['id']     = aid
                temp['angle']  = float(annot_theta)
                annotation_list.append(temp)
            if len(species_list) > 0:
                species = max(set(species_list), key=species_list.count)  # Get most common species
            elif app.default_species is not None:
                species = app.default_species
            else:
                species = KEY_DEFAULTS[SPECIES_KEY]
        else:
            gpath = None
            species = None
            image_src = None
            annotation_list = []
        return ap.template('turk', 'detection',
                           eid=eid,
                           gid=gid,
                           refer_aid=refer_aid,
                           species=species,
                           image_path=gpath,
                           image_src=image_src,
                           previous=previous,
                           enctext=enctext,
                           progress=progress,
                           finished=finished,
                           annotation_list=annotation_list,
                           display_instructions=display_instructions,
                           display_species_examples=display_species_examples,
                           review=review)
    except Exception as e:
        return error404(e)


@app.route('/turk/viewpoint')
def turk_viewpoint():
    try:
        eid = request.args.get('eid', '')
        eid = None if eid == 'None' or eid == '' else int(eid)

        gid_list = app.ibs.get_valid_gids(eid=eid)
        aid_list = ut.flatten(app.ibs.get_image_aids(gid_list))
        reviewed_list = encounter_annot_viewpoint_processed(aid_list)
        progress = '%0.2f' % (100.0 * reviewed_list.count(True) / len(aid_list), )

        enctext = None if eid is None else app.ibs.get_encounter_text(eid)
        aid = request.args.get('aid', '')
        if len(aid) > 0:
            aid = int(aid)
        else:
            aid_list_ = ut.filterfalse_items(aid_list, reviewed_list)
            if len(aid_list_) == 0:
                aid = None
            else:
                # aid = aid_list_[0]
                aid = random.choice(aid_list_)
        previous = request.args.get('previous', None)
        value = convert_yaw_to_old_viewpoint(app.ibs.get_annot_yaws(aid))
        review = 'review' in request.args.keys()
        finished = aid is None
        display_instructions = request.cookies.get('viewpoint_instructions_seen', 0) == 0
        if not finished:
            gid       = app.ibs.get_annot_gids(aid)
            gpath     = app.ibs.get_annot_chip_fpath(aid)
            image     = ap.open_oriented_image(gpath)
            image_src = ap.embed_image_html(image)
        else:
            gid       = None
            gpath     = None
            image_src = None
        return ap.template('turk', 'viewpoint',
                           eid=eid,
                           gid=gid,
                           aid=aid,
                           value=value,
                           image_path=gpath,
                           image_src=image_src,
                           previous=previous,
                           enctext=enctext,
                           progress=progress,
                           finished=finished,
                           display_instructions=display_instructions,
                           review=review)
    except Exception as e:
        return error404(e)


@app.route('/turk/quality')
def turk_quality():
    try:
        eid = request.args.get('eid', '')
        eid = None if eid == 'None' or eid == '' else int(eid)

        gid_list = app.ibs.get_valid_gids(eid=eid)
        aid_list = ut.flatten(app.ibs.get_image_aids(gid_list))
        reviewed_list = encounter_annot_quality_processed(aid_list)
        progress = '%0.2f' % (100.0 * reviewed_list.count(True) / len(aid_list), )

        enctext = None if eid is None else app.ibs.get_encounter_text(eid)
        aid = request.args.get('aid', '')
        if len(aid) > 0:
            aid = int(aid)
        else:
            aid_list_ = ut.filterfalse_items(aid_list, reviewed_list)
            if len(aid_list_) == 0:
                aid = None
            else:
                # aid = aid_list_[0]
                aid = random.choice(aid_list_)
        previous = request.args.get('previous', None)
        value = app.ibs.get_annot_qualities(aid)
        if value == -1:
            value = None
        if value == 0:
            value = 1
        review = 'review' in request.args.keys()
        finished = aid is None
        display_instructions = request.cookies.get('quality_instructions_seen', 0) == 0
        if not finished:
            gid       = app.ibs.get_annot_gids(aid)
            gpath     = app.ibs.get_annot_chip_fpath(aid)
            image     = ap.open_oriented_image(gpath)
            image_src = ap.embed_image_html(image)
        else:
            gid       = None
            gpath     = None
            image_src = None
        return ap.template('turk', 'quality',
                           eid=eid,
                           gid=gid,
                           aid=aid,
                           value=value,
                           image_path=gpath,
                           image_src=image_src,
                           previous=previous,
                           enctext=enctext,
                           progress=progress,
                           finished=finished,
                           display_instructions=display_instructions,
                           review=review)
    except Exception as e:
        return error404(e)


@app.route('/turk/additional')
def turk_additional():
    try:
        eid = request.args.get('eid', '')
        eid = None if eid == 'None' or eid == '' else int(eid)

        gid_list = app.ibs.get_valid_gids(eid=eid)
        aid_list = ut.flatten(app.ibs.get_image_aids(gid_list))
        nid_list = app.ibs.get_annot_nids(aid_list)
        reviewed_list = encounter_annot_additional_processed(aid_list, nid_list)
        progress = '%0.2f' % (100.0 * reviewed_list.count(True) / len(aid_list), )

        enctext = None if eid is None else app.ibs.get_encounter_text(eid)
        aid = request.args.get('aid', '')
        if len(aid) > 0:
            aid = int(aid)
        else:
            aid_list_ = ut.filterfalse_items(aid_list, reviewed_list)
            if len(aid_list_) == 0:
                aid = None
            else:
                # aid = aid_list_[0]
                aid = random.choice(aid_list_)
        previous = request.args.get('previous', None)
        value_sex = app.ibs.get_annot_sex([aid])[0]
        if value_sex >= 0:
            value_sex += 2
        else:
            value_sex = None
        value_age_min, value_age_max = app.ibs.get_annot_age_months_est([aid])[0]
        value_age = None
        if (value_age_min is -1 or value_age_min is None) and (value_age_max is -1 or value_age_max is None):
            value_age = 1
        if (value_age_min is 0 or value_age_min is None) and value_age_max == 2:
            value_age = 2
        elif value_age_min is 3 and value_age_max == 5:
            value_age = 3
        elif value_age_min is 6 and value_age_max == 11:
            value_age = 4
        elif value_age_min is 12 and value_age_max == 23:
            value_age = 5
        elif value_age_min is 24 and value_age_max == 35:
            value_age = 6
        elif value_age_min is 36 and (value_age_max > 36 or value_age_max is None):
            value_age = 7

        review = 'review' in request.args.keys()
        finished = aid is None
        display_instructions = request.cookies.get('additional_instructions_seen', 0) == 0
        if not finished:
            gid       = app.ibs.get_annot_gids(aid)
            gpath     = app.ibs.get_annot_chip_fpath(aid)
            image     = ap.open_oriented_image(gpath)
            image_src = ap.embed_image_html(image)
        else:
            gid       = None
            gpath     = None
            image_src = None
        name_aid_list = None
        nid = app.ibs.get_annot_name_rowids(aid)
        if nid is not None:
            name_aid_list = app.ibs.get_name_aids(nid)
            quality_list = app.ibs.get_annot_qualities(name_aid_list)
            quality_text_list = app.ibs.get_annot_quality_texts(name_aid_list)
            yaw_text_list = app.ibs.get_annot_yaw_texts(name_aid_list)
            name_aid_combined_list = list(zip(
                name_aid_list,
                quality_list,
                quality_text_list,
                yaw_text_list,
            ))

            name_aid_combined_list.sort(key=lambda t: t[1], reverse=True)
        return ap.template('turk', 'additional',
                           eid=eid,
                           gid=gid,
                           aid=aid,
                           value_sex=value_sex,
                           value_age=value_age,
                           image_path=gpath,
                           name_aid_combined_list=name_aid_combined_list,
                           image_src=image_src,
                           previous=previous,
                           enctext=enctext,
                           progress=progress,
                           finished=finished,
                           display_instructions=display_instructions,
                           review=review)
    except Exception as e:
        return error404(e)


@app.route('/submit/detection', methods=['POST'])
def submit_detection():
    try:
        method = request.form.get('detection-submit', '')
        eid = request.args.get('eid', '')
        eid = None if eid == 'None' or eid == '' else int(eid)
        gid = int(request.form['detection-gid'])
        turk_id = request.cookies.get('turk_id', -1)

        if method.lower() == 'delete':
            # app.ibs.delete_images(gid)
            # print('[web] (DELETED) turk_id: %s, gid: %d' % (turk_id, gid, ))
            pass
        elif method.lower() == 'clear':
            aid_list = app.ibs.get_image_aids(gid)
            app.ibs.delete_annots(aid_list)
            print('[web] (CLEAERED) turk_id: %s, gid: %d' % (turk_id, gid, ))
            redirection = request.referrer
            if 'gid' not in redirection:
                # Prevent multiple clears
                if '?' in redirection:
                    redirection = '%s&gid=%d' % (redirection, gid, )
                else:
                    redirection = '%s?gid=%d' % (redirection, gid, )
            return redirect(redirection)
        else:
            current_aid_list = app.ibs.get_image_aids(gid)
            # Make new annotations
            width, height = app.ibs.get_image_sizes(gid)
            scale_factor = float(width) / 700.0
            # Get aids
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
            survived_aid_list = [
                None if annot['id'] is None else int(annot['id'])
                for annot in annotation_list
            ]
            species_list = [
                annot['label']
                for annot in annotation_list
            ]
            # Delete annotations that didn't survive
            kill_aid_list = list(set(current_aid_list) - set(survived_aid_list))
            app.ibs.delete_annots(kill_aid_list)
            for aid, bbox, theta, species in zip(survived_aid_list, bbox_list, theta_list, species_list):
                if aid is None:
                    app.ibs.add_annots([gid], [bbox], theta_list=[theta], species_list=[species])
                else:
                    app.ibs.set_annot_bboxes([aid], [bbox])
                    app.ibs.set_annot_thetas([aid], [theta])
                    app.ibs.set_annot_species([aid], [species])
            app.ibs.set_image_reviewed([gid], [1])
            print('[web] turk_id: %s, gid: %d, bbox_list: %r, species_list: %r' % (turk_id, gid, annotation_list, species_list))
        # Return HTML
        refer = request.args.get('refer', '')
        if len(refer) > 0:
            return redirect(ap.decode_refer_url(refer))
        else:
            return redirect(url_for('turk_detection', eid=eid, previous=gid))
    except Exception as e:
        return error404(e)


@app.route('/submit/viewpoint', methods=['POST'])
def submit_viewpoint():
    try:
        method = request.form.get('viewpoint-submit', '')
        eid = request.args.get('eid', '')
        eid = None if eid == 'None' or eid == '' else int(eid)
        aid = int(request.form['viewpoint-aid'])
        turk_id = request.cookies.get('turk_id', -1)
        if method.lower() == 'delete':
            app.ibs.delete_annots(aid)
            print('[web] (DELETED) turk_id: %s, aid: %d' % (turk_id, aid, ))
            aid = None  # Reset AID to prevent previous
        if method.lower() == 'rotate left':
            theta = app.ibs.get_annot_thetas(aid)
            theta = (theta + const.PI / 2) % const.TAU
            app.ibs.set_annot_thetas(aid, theta)
            (xtl, ytl, w, h) = app.ibs.get_annot_bboxes(aid)
            diffx = int(round((w / 2.0) - (h / 2.0)))
            diffy = int(round((h / 2.0) - (w / 2.0)))
            xtl, ytl, w, h = xtl + diffx, ytl + diffy, h, w
            app.ibs.set_annot_bboxes([aid], [(xtl, ytl, w, h)])
            print('[web] (ROTATED LEFT) turk_id: %s, aid: %d' % (turk_id, aid, ))
            redirection = request.referrer
            if 'aid' not in redirection:
                # Prevent multiple clears
                if '?' in redirection:
                    redirection = '%s&aid=%d' % (redirection, aid, )
                else:
                    redirection = '%s?aid=%d' % (redirection, aid, )
            return redirect(redirection)
        if method.lower() == 'rotate right':
            theta = app.ibs.get_annot_thetas(aid)
            theta = (theta - const.PI / 2) % const.TAU
            app.ibs.set_annot_thetas(aid, theta)
            (xtl, ytl, w, h) = app.ibs.get_annot_bboxes(aid)
            diffx = int(round((w / 2.0) - (h / 2.0)))
            diffy = int(round((h / 2.0) - (w / 2.0)))
            xtl, ytl, w, h = xtl + diffx, ytl + diffy, h, w
            app.ibs.set_annot_bboxes([aid], [(xtl, ytl, w, h)])
            print('[web] (ROTATED RIGHT) turk_id: %s, aid: %d' % (turk_id, aid, ))
            redirection = request.referrer
            if 'aid' not in redirection:
                # Prevent multiple clears
                if '?' in redirection:
                    redirection = '%s&aid=%d' % (redirection, aid, )
                else:
                    redirection = '%s?aid=%d' % (redirection, aid, )
            return redirect(redirection)
        else:
            value = int(request.form['viewpoint-value'])
            yaw = convert_old_viewpoint_to_yaw(value)
            app.ibs.set_annot_yaws([aid], [yaw], input_is_degrees=False)
            print('[web] turk_id: %s, aid: %d, yaw: %d' % (turk_id, aid, yaw))
        # Return HTML
        refer = request.args.get('refer', '')
        if len(refer) > 0:
            return redirect(ap.decode_refer_url(refer))
        else:
            return redirect(url_for('turk_viewpoint', eid=eid, previous=aid))
    except Exception as e:
        return error404(e)


@app.route('/submit/quality', methods=['POST'])
def submit_quality():
    try:
        method = request.form.get('quality-submit', '')
        eid = request.args.get('eid', '')
        eid = None if eid == 'None' or eid == '' else int(eid)
        aid = int(request.form['quality-aid'])
        turk_id = request.cookies.get('turk_id', -1)

        if method.lower() == 'delete':
            app.ibs.delete_annots(aid)
            print('[web] (DELETED) turk_id: %s, aid: %d' % (turk_id, aid, ))
            aid = None  # Reset AID to prevent previous
        else:
            quality = int(request.form['quality-value'])
            app.ibs.set_annot_qualities([aid], [quality])
            print('[web] turk_id: %s, aid: %d, quality: %d' % (turk_id, aid, quality))
        # Return HTML
        refer = request.args.get('refer', '')
        if len(refer) > 0:
            return redirect(ap.decode_refer_url(refer))
        else:
            return redirect(url_for('turk_quality', eid=eid, previous=aid))
    except Exception as e:
        return error404(e)


@app.route('/submit/additional', methods=['POST'])
def submit_additional():
    try:
        method = request.form.get('additional-submit', '')
        eid = request.args.get('eid', '')
        eid = None if eid == 'None' or eid == '' else int(eid)
        aid = int(request.form['additional-aid'])
        turk_id = request.cookies.get('turk_id', -1)

        if method.lower() == 'delete':
            app.ibs.delete_annots(aid)
            print('[web] (DELETED) turk_id: %s, aid: %d' % (turk_id, aid, ))
            aid = None  # Reset AID to prevent previous
        else:
            sex = int(request.form['additional-sex-value'])
            age = int(request.form['additional-age-value'])
            age_min = None
            age_max = None
            # Sex
            if sex >= 2:
                sex -= 2
            else:
                sex = -1

            if age == 1:
                age_min = None
                age_max = None
            elif age == 2:
                age_min = None
                age_max = 2
            elif age == 3:
                age_min = 3
                age_max = 5
            elif age == 4:
                age_min = 6
                age_max = 11
            elif age == 5:
                age_min = 12
                age_max = 23
            elif age == 6:
                age_min = 24
                age_max = 35
            elif age == 7:
                age_min = 36
                age_max = None

            app.ibs.set_annot_sex([aid], [sex])
            nid = app.ibs.get_annot_name_rowids(aid)
            DAN_SPECIAL_WRITE_AGE_TO_ALL_ANOTATIONS = True
            if nid is not None and DAN_SPECIAL_WRITE_AGE_TO_ALL_ANOTATIONS:
                aid_list = app.ibs.get_name_aids(nid)
                app.ibs.set_annot_age_months_est_min(aid_list, [age_min] * len(aid_list))
                app.ibs.set_annot_age_months_est_max(aid_list, [age_max] * len(aid_list))
            else:
                app.ibs.set_annot_age_months_est_min([aid], [age_min])
                app.ibs.set_annot_age_months_est_max([aid], [age_max])
            print('[web] turk_id: %s, aid: %d, sex: %r, age: %r' % (turk_id, aid, sex, age))
        # Return HTML
        refer = request.args.get('refer', '')
        if len(refer) > 0:
            return redirect(ap.decode_refer_url(refer))
        else:
            return redirect(url_for('turk_additional', eid=eid, previous=aid))
    except Exception as e:
        return error404(e)


@app.route('/ajax/cookie')
def set_cookie():
    response = make_response('true')
    try:
        response.set_cookie(request.args['name'], request.args['value'])
        print('[web] Set Cookie: %r -> %r' % (request.args['name'], request.args['value'], ))
        return response
    except:
        print('[web] COOKIE FAILED: %r' % (request.args, ))
        return make_response('false')


@app.route('/ajax/image/src/<gid>')
def image_src(gid=None):
    # gpath = app.ibs.get_image_paths(gid)
    gpath = app.ibs.get_image_thumbpath(gid, ensure_paths=True)
    return ap.return_src(gpath)


@app.route('/ajax/annotation/src/<aid>')
def annotation_src(aid=None):
    gpath = app.ibs.get_annot_chip_fpath(aid)
    return ap.return_src(gpath)


@app.route('/api')
@app.route('/api/<function>.json', methods=['GET', 'POST'])
def api(function=None):
    template = {
        'status': {
            'success': False,
            'code': '',
        },
    }
    print('[web] Function:', function)
    print('[web] POST:', dict(request.form))
    print('[web] GET:',  dict(request.args))
    if function is None:
        template['status']['success'] = True
        template['status']['code'] = 'USAGE: /api/[ibeis_function_name].json'
    else:
        function = function.lower()
        if ap.check_valid_function_name(function):
            function = 'app.ibs.%s' % function
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


@app.route('/display/sightings')
def display_sightings():
    complete = request.args.get('complete', None) is not None
    sightings = app.ibs.report_sightings_str(complete=complete)
    return sightings


@app.route('/download/sightings')
def download_sightings():
    filename = 'sightings.csv'
    sightings = display_sightings()
    return ap.send_file(sightings, filename)


@app.route('/graph/sightings')
def graph_sightings():
    return redirect(url_for('view'))


@app.route('/404')
def error404(exception):
    exception_str = str(exception)
    traceback_str = str(traceback.format_exc())
    print('[web] %r' % (exception_str, ))
    print(traceback_str)
    return ap.template(None, '404', exception_str=exception_str,
                       traceback_str=traceback_str)


################################################################################


def start_tornado(app, port=None, browser=BROWSER, blocking=False, reset_db=True):
    def _start_tornado():
        http_server = tornado.httpserver.HTTPServer(
            tornado.wsgi.WSGIContainer(app))
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    if port is None:
        port = DEFAULT_PORT
    # Initialize the web server
    logging.getLogger().setLevel(logging.INFO)
    try:
        app.server_ip_address = socket.gethostbyname(socket.gethostname())
        app.port = port
    except:
        app.server_ip_address = '127.0.0.1'
        app.port = port
    url = 'http://%s:%s' % (app.server_ip_address, app.port)
    print('[web] Tornado server starting at %s' % (url,))
    if browser:
        import webbrowser
        webbrowser.open(url)
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
        type='int', default=None)
    parser.add_option(
        '--db',
        help='specify an IBEIS database',
        type='str', default='testdb0')

    opts, args = parser.parse_args()
    app.ibs = ibeis.opendb(db=opts.db)
    print('[web] Pre-computing all image thumbnails...')
    app.ibs.compute_all_thumbs()
    print('[web] Pre-computing all image thumbnails (without annots)...')
    app.ibs.compute_all_thumbs(draw_annots=False)
    print('[web] Pre-computing all annotation chips...')
    app.ibs.check_chip_existence()
    app.ibs.compute_all_chips()
    start_tornado(app, opts.port)


def start_from_ibeis(ibs, port=None):
    '''
    Parse command line options and start the server.
    '''
    dbname = ibs.get_dbname()
    if dbname == 'CHTA_Master':
        app.default_species = Species.CHEETAH
    elif dbname == 'ELPH_Master':
        app.default_species = Species.ELEPHANT_SAV
    elif dbname == 'GIR_Master':
        app.default_species = Species.GIRAFFE
    elif dbname == 'GZ_Master':
        app.default_species = Species.ZEB_GREVY
    elif dbname == 'LION_Master':
        app.default_species = Species.LION
    elif dbname == 'PZ_Master':
        app.default_species = Species.ZEB_PLAIN
    elif dbname == 'WD_Master':
        app.default_species = Species.WILDDOG
    elif dbname == 'NNP_MasterGIRM':
        app.default_species = Species.GIRAFFE_MASAI
    elif 'NNP_' in dbname:
        app.default_species = Species.ZEB_PLAIN
    elif 'GZC' in dbname:
        app.default_species = Species.ZEB_PLAIN
    else:
        app.default_species = None
    print('[web] DEFAULT SPECIES: %r' % (app.default_species))
    app.ibs = ibs
    print('[web] Pre-computing all image thumbnails (with annots)...')
    app.ibs.compute_all_thumbs()
    print('[web] Pre-computing all image thumbnails (without annots)...')
    app.ibs.compute_all_thumbs(draw_annots=False)
    print('[web] Pre-computing all annotation chips...')
    app.ibs.check_chip_existence()
    app.ibs.compute_all_chips()
    start_tornado(app, port)


if __name__ == '__main__':
    start_from_terminal()
