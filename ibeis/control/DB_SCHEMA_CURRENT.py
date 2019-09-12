"""
AUTOGENERATED ON 12:59:48 2019/07/09
AutogenCommandLine:
    python -m ibeis.control.DB_SCHEMA --test-autogen_db_schema --force-incremental-db-update --write
    python -m ibeis.control.DB_SCHEMA --test-autogen_db_schema --force-incremental-db-update --diff=1
    python -m ibeis.control.DB_SCHEMA --test-autogen_db_schema --force-incremental-db-update
"""
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import utool as ut
(print, rrr, profile) = ut.inject2(__name__)

# =======================
# Schema Version Current
# =======================


VERSION_CURRENT = '2.0.0.vulcan'


def update_current(db, ibs=None):
    db.add_table('annotation_lblannot_relationship', [
        ('alr_rowid',                    'INTEGER PRIMARY KEY'),
        ('annot_rowid',                  'INTEGER NOT NULL'),
        ('lblannot_rowid',               'INTEGER NOT NULL'),
        ('alr_confidence',               'REAL DEFAULT 0.0'),
    ],
        docstr='''
        Used to store one-to-many the relationship between annotations
        (annots) and labels
        ''',
        superkeys=[('annot_rowid', 'lblannot_rowid')],
        relates=('annotations', 'lblannot'),
        shortname='alr',
    )

    db.add_table('annotations', [
        ('annot_rowid',                  'INTEGER PRIMARY KEY'),
        ('annot_parent_rowid',           'INTEGER'),
        ('annot_uuid',                   'UUID NOT NULL'),
        ('image_rowid',                  'INTEGER NOT NULL'),
        ('annot_xtl',                    'INTEGER NOT NULL'),
        ('annot_ytl',                    'INTEGER NOT NULL'),
        ('annot_width',                  'INTEGER NOT NULL'),
        ('annot_height',                 'INTEGER NOT NULL'),
        ('annot_theta',                  'REAL DEFAULT 0.0'),
        ('annot_num_verts',              'INTEGER NOT NULL'),
        ('annot_verts',                  'TEXT'),
        ('annot_yaw',                    'REAL'),
        ('annot_viewpoint',              'TEXT'),
        ('annot_detect_confidence',      'REAL DEFAULT -1.0'),
        ('annot_toggle_reviewed',        'INTEGER DEFAULT 0'),
        ('annot_toggle_multiple',        'INTEGER DEFAULT NULL'),
        ('annot_toggle_interest',        'INTEGER DEFAULT NULL'),
        ('annot_toggle_canonical',       'INTEGER DEFAULT NULL'),
        ('annot_exemplar_flag',          'INTEGER DEFAULT 0'),
        ('annot_note',                   'TEXT'),
        ('annot_visual_uuid',            'UUID NOT NULL'),
        ('annot_semantic_uuid',          'UUID'),
        ('name_rowid',                   'INTEGER DEFAULT 0'),
        ('species_rowid',                'INTEGER DEFAULT 0'),
        ('annot_quality',                'INTEGER'),
        ('contributor_rowid',            'INTEGER'),
        ('annot_age_months_est_min',     'INTEGER DEFAULT -1'),
        ('annot_age_months_est_max',     'INTEGER DEFAULT -1'),
        ('annot_tag_text',               'TEXT'),
        ('annot_metadata_json',          'TEXT'),
        ('annot_static_encounter',       'TEXT'),
        ('annot_viewpoint_int',          'INTEGER'),
        ('annot_staged_flag',            'INTEGER DEFAULT 0'),
        ('annot_staged_uuid',            'UUID'),
        ('annot_staged_user_identity',   'TEXT'),
        ('annot_staged_metadata_json',   'TEXT'),
    ],
        docstr='''
        Mainly used to store the geometry of the annotation within its parent
        image The one-to-many relationship between images and annotations is
        encoded here
        ''',
        superkeys=[('annot_uuid',), ('annot_visual_uuid', 'annot_staged_uuid')],
        shortname='annot',
        extern_tables=['names', 'species', 'images'],
        primary_superkey=('annot_uuid',),
        dependsmap={
            'annot_parent_rowid': ('annotations', ('annot_rowid',), ('annot_visual_uuid',)),
            'contributor_rowid' : ('contributors', None, None),
            'image_rowid'       : ('images', ('image_rowid',), ('image_uuid',)),
            'name_rowid'        : ('names', ('name_rowid',), ('name_text',)),
            'species_rowid'     : ('species', ('species_rowid',), ('species_text',)),
    },
    )

    db.add_table('annotgroup_annotation_relationship', [
        ('gar_rowid',                    'INTEGER PRIMARY KEY'),
        ('annotgroup_rowid',             'INTEGER NOT NULL'),
        ('annot_rowid',                  'INTEGER'),
    ],
        docstr='''
        Relationship between annotgroups and annots (many to many mapping) the
        many-to-many relationship between annots and annotgroups is encoded
        here annotgroup_annotation_relationship stands for annotgroup-
        annotation-pairs.
        ''',
        superkeys=[('annotgroup_rowid', 'annot_rowid')],
    )

    db.add_table('annotgroups', [
        ('annotgroup_rowid',             'INTEGER PRIMARY KEY'),
        ('annotgroup_uuid',              'UUID NOT NULL'),
        ('annotgroup_text',              'TEXT NOT NULL'),
        ('annotgroup_note',              'TEXT NOT NULL'),
    ],
        docstr='''
        List of all annotation groups (annotgroups)
        ''',
        superkeys=[('annotgroup_text',)],
    )

    db.add_table('annotmatch', [
        ('annotmatch_rowid',              'INTEGER PRIMARY KEY'),
        ('annot_rowid1',                  'INTEGER NOT NULL'),
        ('annot_rowid2',                  'INTEGER NOT NULL'),
        ('annotmatch_evidence_decision',  'INTEGER'),
        ('annotmatch_confidence',         'INTEGER'),
        ('annotmatch_tag_text',           'TEXT'),
        ('annotmatch_reviewer',           'TEXT'),
        ('annotmatch_posixtime_modified', 'INTEGER'),
        ('annotmatch_count',              'INTEGER'),
        ('annotmatch_meta_decision',      'INTEGER'),
    ],
        docstr='''
        Sparsely stores explicit matching / not matching information. This
        serves as marking weather or not an annotation pair has been reviewed.
        ''',
        superkeys=[('annot_rowid1', 'annot_rowid2')],
        relates=('annotations', 'annotations'),
        dependsmap={
            'annot_rowid1': ('annotations', ('annot_rowid',), ('annot_visual_uuid',)),
            'annot_rowid2': ('annotations', ('annot_rowid',), ('annot_visual_uuid',)),
    },
    )

    db.add_table('contributors', [
        ('contributor_rowid',            'INTEGER PRIMARY KEY'),
        ('contributor_uuid',             'UUID NOT NULL'),
        ('contributor_tag',              'TEXT'),
        ('contributor_name_first',       'TEXT'),
        ('contributor_name_last',        'TEXT'),
        ('contributor_location_city',    'TEXT'),
        ('contributor_location_state',   'TEXT'),
        ('contributor_location_country', 'TEXT'),
        ('contributor_location_zip',     'TEXT'),
        ('contributor_note',             'TEXT'),
    ],
        docstr='''
        Used to store the contributors to the project
        ''',
        superkeys=[('contributor_tag',)],
    )

    db.add_table('image_lblimage_relationship', [
        ('glr_rowid',                    'INTEGER PRIMARY KEY'),
        ('image_rowid',                  'INTEGER NOT NULL'),
        ('lblimage_rowid',               'INTEGER NOT NULL'),
        ('glr_confidence',               'REAL DEFAULT 0.0'),
    ],
        docstr='''
        Used to store one-to-many the relationship between images and labels
        ''',
        superkeys=[('image_rowid', 'lblimage_rowid')],
        relates=('images', 'lblimage'),
        shortname='glr',
    )

    db.add_table('images', [
        ('image_rowid',                  'INTEGER PRIMARY KEY'),
        ('contributor_rowid',            'INTEGER'),
        ('image_uuid',                   'UUID NOT NULL'),
        ('image_uri',                    'TEXT NOT NULL'),
        ('image_uri_original',           'TEXT NOT NULL'),
        ('image_ext',                    'TEXT NOT NULL'),
        ('image_original_name',          'TEXT NOT NULL'),
        ('image_width',                  'INTEGER DEFAULT -1'),
        ('image_height',                 'INTEGER DEFAULT -1'),
        ('image_time_posix',             'INTEGER DEFAULT -1'),
        ('image_gps_lat',                'REAL DEFAULT -1.0'),
        ('image_gps_lon',                'REAL DEFAULT -1.0'),
        ('image_orientation',            'INTEGER DEFAULT 0'),
        ('image_toggle_enabled',         'INTEGER DEFAULT 0'),
        ('image_toggle_reviewed',        'INTEGER DEFAULT 0'),
        ('image_toggle_cameratrap',      'INTEGER DEFAULT NULL'),
        ('image_note',                   'TEXT'),
        ('image_timedelta_posix',        'INTEGER DEFAULT 0'),
        ('image_original_path',          'TEXT'),
        ('image_location_code',          'TEXT'),
        ('party_rowid',                  'INTEGER'),
        ('image_metadata_json',          'TEXT'),
        ('image_tile_parent_rowid',      'INTEGER'),
        ('image_tile_xtl',               'INTEGER'),
        ('image_tile_ytl',               'INTEGER'),
        ('image_tile_width',             'INTEGER'),
        ('image_tile_height',            'INTEGER'),
        ('image_tile_border_flag',       'INTEGER'),
        ('image_tile_config_json',       'TEXT'),
        ('image_tile_config_hashid',     'TEXT'),
    ],
        docstr='''
        First class table used to store image locations and meta-data
        ''',
        superkeys=[('image_uuid',)],
        shortname='image',
        extern_tables=['party', 'contributors'],
        dependsmap={
            'contributor_rowid': ('contributors', ('contributor_rowid',), ('contributor_tag',)),
            'party_rowid'      : ('party', ('party_rowid',), ('party_tag',)),
    },
    )

    db.add_table('imageset_image_relationship', [
        ('gsgr_rowid',                   'INTEGER PRIMARY KEY'),
        ('image_rowid',                  'INTEGER NOT NULL'),
        ('imageset_rowid',               'INTEGER'),
    ],
        docstr='''
        Relationship between imagesets and images (many to many mapping) the
        many-to-many relationship between images and imagesets is encoded here
        imageset_image_relationship stands for imageset-image-pairs.
        ''',
        superkeys=[('image_rowid', 'imageset_rowid')],
        relates=('images', 'imagesets'),
        shortname='gsgr',
        dependsmap={
            'image_rowid'   : ('images', ('image_rowid',), ('image_uuid',)),
            'imageset_rowid': ('imagesets', ('imageset_rowid',), ('imageset_text',)),
    },
    )

    db.add_table('imagesets', [
        ('imageset_rowid',               'INTEGER PRIMARY KEY'),
        ('imageset_uuid',                'UUID NOT NULL'),
        ('imageset_text',                'TEXT NOT NULL'),
        ('imageset_occurrence_flag',     'INTEGER DEFAULT 0'),
        ('imageset_note',                'TEXT NOT NULL'),
        ('imageset_start_time_posix',    'INTEGER'),
        ('imageset_end_time_posix',      'INTEGER'),
        ('imageset_gps_lat',             'INTEGER'),
        ('imageset_gps_lon',             'INTEGER'),
        ('imageset_processed_flag',      'INTEGER DEFAULT 0'),
        ('imageset_shipped_flag',        'INTEGER DEFAULT 0'),
        ('imageset_smart_xml_fname',     'TEXT'),
        ('imageset_smart_waypoint_id',   'INTEGER'),
        ('imageset_metadata_json',       'TEXT'),
    ],
        docstr='''
        List of all imagesets. This used to be called the encounter table. It
        represents a group of potentially many individuals seen in a specific
        place at a specific time.
        ''',
        superkeys=[('imageset_text',)],
        dependsmap={},
    )

    db.add_table('keys', [
        ('lbltype_rowid',                'INTEGER PRIMARY KEY'),
        ('lbltype_text',                 'TEXT NOT NULL'),
        ('lbltype_default',              'TEXT NOT NULL'),
    ],
        docstr='''
        List of keys used to define the categories of annotation lables, text
        is for human-readability. The lbltype_default specifies the
        lblannot_value of annotations with a relationship of some
        lbltype_rowid
        ''',
        superkeys=[('lbltype_text',)],
    )

    db.add_table('lblannot', [
        ('lblannot_rowid',               'INTEGER PRIMARY KEY'),
        ('lblannot_uuid',                'UUID NOT NULL'),
        ('lbltype_rowid',                'INTEGER NOT NULL'),
        ('lblannot_value',               'TEXT NOT NULL'),
        ('lblannot_note',                'TEXT'),
    ],
        docstr='''
        Used to store the labels / attributes of annotations. E.G name,
        species
        ''',
        superkeys=[('lbltype_rowid', 'lblannot_value')],
    )

    db.add_table('lblimage', [
        ('lblimage_rowid',               'INTEGER PRIMARY KEY'),
        ('lblimage_uuid',                'UUID NOT NULL'),
        ('lbltype_rowid',                'INTEGER NOT NULL'),
        ('lblimage_value',               'TEXT NOT NULL'),
        ('lblimage_note',                'TEXT'),
    ],
        docstr='''
        Used to store the labels (attributes) of images
        ''',
        superkeys=[('lbltype_rowid', 'lblimage_value')],
    )

    db.add_table('metadata', [
        ('metadata_rowid',               'INTEGER PRIMARY KEY'),
        ('metadata_key',                 'TEXT'),
        ('metadata_value',               'TEXT'),
    ],
        docstr='''
        The table that stores permanently all of the metadata about the
        database (tables, etc)
        ''',
        superkeys=[('metadata_key',)],
    )

    db.add_table('names', [
        ('name_rowid',                   'INTEGER PRIMARY KEY'),
        ('name_uuid',                    'UUID NOT NULL'),
        ('name_text',                    'TEXT NOT NULL'),
        ('name_note',                    'TEXT'),
        ('name_temp_flag',               'INTEGER DEFAULT 0'),
        ('name_alias_text',              'TEXT'),
        ('name_sex',                     'INTEGER DEFAULT -1'),
        ('name_metadata_json',           'TEXT'),
    ],
        docstr='''
        Stores the individual animal names
        ''',
        superkeys=[('name_text',)],
    )

    db.add_table('parts', [
        ('part_rowid',                   'INTEGER PRIMARY KEY'),
        ('part_uuid',                    'UUID NOT NULL'),
        ('annot_rowid',                  'INTEGER NOT NULL'),
        ('part_xtl',                     'INTEGER NOT NULL'),
        ('part_ytl',                     'INTEGER NOT NULL'),
        ('part_width',                   'INTEGER NOT NULL'),
        ('part_height',                  'INTEGER NOT NULL'),
        ('part_theta',                   'REAL DEFAULT 0.0'),
        ('part_num_verts',               'INTEGER NOT NULL'),
        ('part_verts',                   'TEXT'),
        ('part_viewpoint',               'TEXT'),
        ('part_detect_confidence',       'REAL DEFAULT -1.0'),
        ('part_toggle_reviewed',         'INTEGER DEFAULT 0'),
        ('part_quality',                 'INTEGER'),
        ('part_type',                    'TEXT'),
        ('part_note',                    'TEXT'),
        ('part_tag_text',                'TEXT'),
        ('part_staged_flag',             'INTEGER DEFAULT 0'),
        ('part_staged_uuid',             'UUID'),
        ('part_staged_user_identity',    'TEXT'),
        ('part_staged_metadata_json',    'TEXT'),
        ('part_metadata_json',           'TEXT'),
        ('part_contour_json',            'TEXT'),
    ],
        docstr='''
        Mainly used to store the geometry of the annotation parts within its
        parent annotation. The one-to-many relationship between annotations
        and parts is encoded here
        ''',
        superkeys=[('part_uuid',)],
        shortname='part',
        extern_tables=['annotations'],
        dependsmap={
            'annot_rowid': ('annotations', ('annot_rowid',), ('annot_uuid',)),
    },
    )

    db.add_table('party', [
        ('party_rowid',                  'INTEGER PRIMARY KEY'),
        ('party_tag',                    'TEXT NOT NULL'),
    ],
        docstr='''
        Serves as a group for contributors
        ''',
        superkeys=[('party_tag',)],
    )

    db.add_table('species', [
        ('species_rowid',                'INTEGER PRIMARY KEY'),
        ('species_uuid',                 'UUID NOT NULL'),
        ('species_text',                 'TEXT NOT NULL'),
        ('species_nice',                 'TEXT NOT NULL'),
        ('species_code',                 'TEXT NOT NULL'),
        ('species_note',                 'TEXT'),
        ('species_toggle_enabled',       'INTEGER DEFAULT 1'),
    ],
        docstr='''
        Stores the different animal species
        ''',
        superkeys=[('species_text',)],
    )
