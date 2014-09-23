"""
#=================
# pipeline:
# Module Concepts
#=================

PREFIXES:
qaid2_XXX - prefix mapping query chip index to
qfx2_XXX  - prefix mapping query chip feature index to

TUPLES:
 * nns    - a (qfx2_idx, qfx2_dist) tuple
 * nnfilt - a (qfx2_fs, qfx2_valid) tuple

SCALARS
 * idx    - the index into the nnindexers descriptors
 * dist   - the distance to a corresponding feature
 * fs     - a score of a corresponding feature
 * valid  - a valid bit for a corresponding feature

REALIZATIONS:
qaid2_nns - maping from query chip index to nns
{
 * qfx2_idx   - ranked list of query feature indexes to database feature indexes
 * qfx2_dist - ranked list of query feature indexes to database feature indexes
}

* qaid2_norm_weight - mapping from qaid to (qfx2_normweight, qfx2_selnorm)
         = qaid2_nnfilt[qaid]
"""
from __future__ import absolute_import, division, print_function
# Python
from six.moves import zip, range
import six
from collections import defaultdict
import sys
# Scientific
import numpy as np
from vtool import keypoint as ktool
from vtool import spatial_verification as sver
# Hotspotter
from ibeis.model.hots import hots_query_result
#from ibeis.model.hots import coverage_image
from ibeis.model.hots import nn_weights
from ibeis.model.hots import voting_rules2 as vr2
from ibeis.model.hots import exceptions as hsexcept
import utool
from functools import partial
#profile = utool.profile
print, print_,  printDBG, rrr, profile = utool.inject(__name__, '[hs]', DEBUG=False)


TAU = 2 * np.pi  # tauday.com
NOT_QUIET = utool.NOT_QUIET and not utool.get_flag('--quiet-query')
VERBOSE = utool.VERBOSE or utool.get_flag('--verbose-query')

#=================
# Globals
#=================

START_AFTER = 2


# specialized progress func
log_progress = partial(utool.log_progress, startafter=START_AFTER, disable=utool.QUIET)


# Query Level 0
#@utool.indent_func('[Q0]')
#@profile
@profile
def request_ibeis_query_L0(ibs, qreq_):
    """
    >>> from ibeis.model.hots.pipeline import *  # NOQA
    #>>> from ibeis.model.hots import match_chips4 as mc4
    >>> from ibeis.model.hots import query_request
    >>> import ibeis
    >>> qaid_list = [1]
    >>> daid_list = [1, 2, 3, 4, 5]
    >>> ibs = ibeis.test_main(db='testdb1')  #doctest: +ELLIPSIS
    >>> qreq_ = query_request.new_ibeis_query_request(ibs, qaid_list, daid_list)
    >>> qaid2_qres = request_ibeis_query_L0(ibs, qreq_)
    >>> qres = qaid2_qres[1]

    Driver logic of query pipeline
    Input:
        ibs   - HotSpotter database object to be queried
        qreq_ - QueryRequest Object   # use prep_qreq to create one
    Output:
        qaid2_qres - mapping from query indexes to Query Result Objects
    """

    # Load data for nearest neighbors
    qreq_.lazy_load(ibs)

    #
    if qreq_.qparams.pipeline_root == 'smk':
        from ibeis.model.hots.smk import smk_index
        daids = qreq_.get_external_daids()
        annots_df = smk_index.make_annot_df(ibs)
        taids = ibs.get_valid_aids()  # exemplar
        # Learn vocabulary
        nWords = qreq_.qparams.nWords
        aggregate = qreq_.qparams.aggregate
        words = smk_index.learn_visual_words(annots_df, taids, nWords)
        # Index a database of annotations
        invindex = smk_index.index_data_annots(annots_df, daids, words,
                                               aggregate=aggregate)
        return smk_index.query_smk(ibs, annots_df, invindex, qreq_)
    else:
        # Nearest neighbors (qaid2_nns)
        # * query descriptors assigned to database descriptors
        # * FLANN used here
        qaid2_nns_ = nearest_neighbors(qreq_)

        # Nearest neighbors weighting and scoring (filt2_weights, filt2_meta)
        # * feature matches are weighted
        filt2_weights_, filt2_meta_ = weight_neighbors(qaid2_nns_, qreq_)

        # Thresholding and weighting (qaid2_nnfilter)
        # * feature matches are pruned
        qaid2_nnfilt_ = filter_neighbors(qaid2_nns_, filt2_weights_, qreq_)

        # Nearest neighbors to chip matches (qaid2_chipmatch)
        # * Inverted index used to create aid2_fmfsfk (TODO: aid2_fmfv)
        # * Initial scoring occurs
        # * vsone inverse swapping occurs here
        qaid2_chipmatch_FILT_ = build_chipmatches(qaid2_nns_, qaid2_nnfilt_, qreq_)

    # Spatial verification (qaid2_chipmatch) (TODO: cython)
    # * prunes chip results and feature matches
    qaid2_chipmatch_SVER_ = spatial_verification(qaid2_chipmatch_FILT_, qreq_)

    # Query results format (qaid2_qres)
    # * Final Scoring. Prunes chip results.
    # * packs into a wrapped query result object
    qaid2_qres_ = chipmatch_to_resdict(qaid2_chipmatch_SVER_, filt2_meta_, qreq_)

    return qaid2_qres_

#============================
# 1) Nearest Neighbors
#============================


@profile
def nearest_neighbors(qreq_):
    """ Plain Nearest Neighbors
    Input:
        qreq_  - a QueryRequest object
    Output:
        qaid2_nnds - a dict mapping query annnotation-ids to a nearest neighbor
                     tuple (indexes, dists). indexes and dist have the shape
                     (nDesc x K) where nDesc is the number of descriptors in the
                     annotation, and K is the number of approximate nearest
                     neighbors.
    """
    # Neareset neighbor configuration
    K      = qreq_.qparams.K
    Knorm  = qreq_.qparams.Knorm
    checks = qreq_.qparams.checks
    if NOT_QUIET:
        print('[hs] Step 1) Assign nearest neighbors: ' + qreq_.qparams.nn_cfgstr)
    num_neighbors = K + Knorm  # number of nearest neighbors
    qvecs_list = qreq_.get_internal_qvecs()  # query descriptors
    # Allocate numpy array for each query annotation
    # TODO: dtype=np.ndarray is just an object, might be useful to use
    # pointers?
    nQAnnots = len(qvecs_list)
    nn_idxs_arr   = np.empty(nQAnnots, dtype=np.ndarray)  # database indexes
    nn_dists_arr = np.empty(nQAnnots, dtype=np.ndarray)  # corresponding distance
    # Internal statistics reporting
    nTotalNN, nTotalDesc = 0, 0
    mark_, end_ = log_progress('Assign NN: ', len(qvecs_list))
    for count, qfx2_vec in enumerate(qvecs_list):
        mark_(count)  # progress
        # Check that we can query this annotation
        if len(qfx2_vec) == 0:
            # Assign empty nearest neighbors
            (qfx2_idx, qfx2_dist) = qreq_.indexer.empty_neighbors(num_neighbors)
        else:
            # Find Neareset Neighbors nntup = (indexes, dists)
            (qfx2_idx, qfx2_dist) = qreq_.indexer.knn(qfx2_vec, num_neighbors, checks)
            nTotalNN += qfx2_idx.size
            nTotalDesc += len(qfx2_vec)
        # record number of query and result desc
        nn_idxs_arr[count]   = qfx2_idx
        nn_dists_arr[count] = qfx2_dist
    end_()
    if NOT_QUIET:
        print('[hs] * assigned %d desc (from %d annots) to %r nearest neighbors'
              % (nTotalDesc, nQAnnots, nTotalNN))
    #return nn_idxs_arr, nn_dists_arr
    # Return old style dicts for now
    qaids = qreq_.get_internal_qaids()
    qaid2_nns_ = {aid: (qfx2_idx, qfx2_dist) for (aid, qfx2_idx, qfx2_dist) in
                  zip(qaids, nn_idxs_arr, nn_dists_arr)}
    return qaid2_nns_


#============================
# 2) Nearest Neighbor weights
#============================


def weight_neighbors(qaid2_nns, qreq_):
    if NOT_QUIET:
        print('[hs] Step 2) Weight neighbors: ' + qreq_.qparams.filt_cfgstr)
    if not qreq_.qparams.filt_on:
        return  {}
    else:
        return _weight_neighbors(qaid2_nns, qreq_)


@profile
def _weight_neighbors(qaid2_nns, qreq_):
    nnweight_list = qreq_.qparams.active_filter_list
    filt2_weights = {}
    filt2_meta = {}
    for nnfilter in nnweight_list:
        nn_filter_fn = nn_weights.NN_WEIGHT_FUNC_DICT[nnfilter]
        # Apply [nnfilter] weight to each nearest neighbor
        # TODO FIX THIS!
        qaid2_norm_weight, qaid2_selnorms = nn_filter_fn(qaid2_nns, qreq_)
        filt2_weights[nnfilter] = qaid2_norm_weight
        filt2_meta[nnfilter] = qaid2_selnorms
    return filt2_weights, filt2_meta


#==========================
# 3) Neighbor scoring (Voting Profiles)
#==========================


@profile
def _threshold_and_scale_weights(qaid, qfx2_nnidx, filt2_weights, qreq_):
    qfx2_score = np.ones(qfx2_nnidx.shape, dtype=hots_query_result.FS_DTYPE)
    qfx2_valid = np.ones(qfx2_nnidx.shape, dtype=np.bool)
    # Apply the filter weightings to determine feature validity and scores
    for filt, aid2_weights in six.iteritems(filt2_weights):
        qfx2_weights = aid2_weights[qaid]
        sign, thresh, weight = qreq_.qparams.filt2_stw[filt]  # stw = sign, thresh, weight
        if thresh is not None:
            qfx2_passed = sign * qfx2_weights <= sign * thresh
            qfx2_valid  = np.logical_and(qfx2_valid, qfx2_passed)
        if not weight == 0:
            qfx2_score += weight * qfx2_weights
    return qfx2_score, qfx2_valid


@profile
def filter_neighbors(qaid2_nns, filt2_weights, qreq_):
    qaid2_nnfilt = {}
    # Configs
    cant_match_sameimg  = not qreq_.qparams.can_match_sameimg
    cant_match_samename = not qreq_.qparams.can_match_samename
    cant_match_self     = not cant_match_sameimg
    K = qreq_.qparams.K
    if NOT_QUIET:
        print('[hs] Step 3) Filter neighbors: ')
    # Filter matches based on config and weights
    mark_, end_ = log_progress('Filter NN: ', len(qaid2_nns))
    for count, qaid in enumerate(six.iterkeys(qaid2_nns)):
        mark_(count)  # progress
        (qfx2_idx, _) = qaid2_nns[qaid]
        qfx2_nnidx = qfx2_idx[:, 0:K]
        # Get a numeric score score and valid flag for each feature match
        qfx2_score, qfx2_valid = _threshold_and_scale_weights(qaid, qfx2_nnidx, filt2_weights, qreq_)
        qfx2_aid = qreq_.indexer.get_nn_aids(qfx2_nnidx)
        if VERBOSE:
            print('[hs] * %d assignments are invalid by thresh' %
                  ((True - qfx2_valid).sum()))
        if qreq_.qparams.gravity_weighting:
            raise NotImplementedError('have not finished gv weighting')
            #from vtool import linalg as ltool
            #qfx2_nnkpts = qreq_.indexer.get_nn_kpts(qfx2_nnidx)
            #qfx2_nnori = ktool.get_oris(qfx2_nnkpts)
            #qfx2_kpts  = qreq_.get_annot_kpts(qaid)  # FIXME: Highly inefficient
            #qfx2_oris  = ktool.get_oris(qfx2_kpts)
            ## Get the orientation distance
            #qfx2_oridist = ltool.rowwise_oridist(qfx2_nnori, qfx2_oris)
            ## Normalize into a weight (close orientations are 1, far are 0)
            #qfx2_gvweight = (TAU - qfx2_oridist) / TAU
            ## Apply gravity vector weight to the score
            #qfx2_score *= qfx2_gvweight
        # Remove Impossible Votes:
        # dont vote for yourself or another chip in the same image
        if cant_match_self:
            qfx2_notsamechip = qfx2_aid != qaid
            ####DBG
            if VERBOSE:
                __self_verbose_check(qfx2_notsamechip, qfx2_valid)
            ####
            qfx2_valid = np.logical_and(qfx2_valid, qfx2_notsamechip)
        if cant_match_sameimg:
            qfx2_gid = qreq_.get_annot_gids(qfx2_aid)
            qgid     = qreq_.get_annot_gids(qaid)
            qfx2_notsameimg = qfx2_gid != qgid
            ####DBG
            if VERBOSE:
                __samename_verbose_check(qfx2_notsameimg, qfx2_valid)
            ####
            qfx2_valid = np.logical_and(qfx2_valid, qfx2_notsameimg)
        if cant_match_samename:
            qfx2_nid = qreq_.get_annot_nids(qfx2_aid)
            qnid = qreq_.get_annot_nids(qaid)
            qfx2_notsamename = qfx2_nid != qnid
            ####DBG
            if VERBOSE:
                __samename_verbose_check(qfx2_notsamename, qfx2_valid)
            ####
            qfx2_valid = np.logical_and(qfx2_valid, qfx2_notsamename)
        #printDBG('[hs] * Marking %d assignments as invalid' % ((True - qfx2_valid).sum()))
        qaid2_nnfilt[qaid] = (qfx2_score, qfx2_valid)
    end_()
    return qaid2_nnfilt


def __self_verbose_check(qfx2_notsamechip, qfx2_valid):
    nChip_all_invalid = ((True - qfx2_notsamechip)).sum()
    nChip_new_invalid = (qfx2_valid * (True - qfx2_notsamechip)).sum()
    print('[hs] * %d assignments are invalid by self' % nChip_all_invalid)
    print('[hs] * %d are newly invalided by self' % nChip_new_invalid)


def __samename_verbose_check(qfx2_notsamename, qfx2_valid):
    nName_all_invalid = ((True - qfx2_notsamename)).sum()
    nName_new_invalid = (qfx2_valid * (True - qfx2_notsamename)).sum()
    print('[hs] * %d assignments are invalid by nid' % nName_all_invalid)
    print('[hs] * %d are newly invalided by nid' % nName_new_invalid)


def __sameimg_verbose_check(qfx2_notsameimg, qfx2_valid):
    nImg_all_invalid = ((True - qfx2_notsameimg)).sum()
    nImg_new_invalid = (qfx2_valid * (True - qfx2_notsameimg)).sum()
    print('[hs] * %d assignments are invalid by gid' % nImg_all_invalid)
    print('[hs] * %d are newly invalided by gid' % nImg_new_invalid)


def identity_filter(qaid2_nns, qreq_):
    """ testing function returns unfiltered nearest neighbors
    this does check that you are not matching yourself
    """
    K = qreq_.qparams.K
    qaid2_nnfilt = {}
    for count, qaid in enumerate(six.iterkeys(qaid2_nns)):
        (qfx2_idx, _) = qaid2_nns[qaid]
        qfx2_nnidx = qfx2_idx[:, 0:K]
        qfx2_score = np.ones(qfx2_nnidx.shape, dtype=hots_query_result.FS_DTYPE)
        qfx2_valid = np.ones(qfx2_nnidx.shape, dtype=np.bool)
        # Check that you are not matching yourself
        qfx2_aid = qreq_.indexer.get_nn_aids(qfx2_nnidx)
        qfx2_notsamechip = qfx2_aid != qaid
        qfx2_valid = np.logical_and(qfx2_valid, qfx2_notsamechip)
        qaid2_nnfilt[qaid] = (qfx2_score, qfx2_valid)
    return qaid2_nnfilt


#============================
# 4) Conversion from featurematches to chipmatches qfx2 -> aid2
#============================


@profile
def _fix_fmfsfk(aid2_fm, aid2_fs, aid2_fk):
    minMatches = 2  # TODO: paramaterize
    # Convert to numpy
    fm_dtype = hots_query_result.FM_DTYPE
    fs_dtype = hots_query_result.FS_DTYPE
    fk_dtype = hots_query_result.FK_DTYPE
    # FIXME: This is slow
    aid2_fm_ = {aid: np.array(fm, fm_dtype)
                for aid, fm in six.iteritems(aid2_fm)
                if len(fm) > minMatches}
    aid2_fs_ = {aid: np.array(fs, fs_dtype)
                for aid, fs in six.iteritems(aid2_fs)
                if len(fs) > minMatches}
    aid2_fk_ = {aid: np.array(fk, fk_dtype)
                for aid, fk in six.iteritems(aid2_fk)
                if len(fk) > minMatches}
    # Ensure shape
    for aid, fm in six.iteritems(aid2_fm_):
        fm.shape = (fm.size // 2, 2)
    chipmatch = (aid2_fm_, aid2_fs_, aid2_fk_)
    return chipmatch


def new_fmfsfk():
    aid2_fm = defaultdict(list)
    aid2_fs = defaultdict(list)
    aid2_fk = defaultdict(list)
    return aid2_fm, aid2_fs, aid2_fk


@profile
def build_chipmatches(qaid2_nns, qaid2_nnfilt, qreq_):
    """
    Input:
        qaid2_nns    - dict of assigned nearest features (only indexes are used here)
        qaid2_nnfilt - dict of (featmatch_scores, featmatch_mask)
                        where the scores and matches correspond to the assigned
                        nearest features
        qreq_         - QueryRequest object

    Output:
        qaid2_chipmatch - dict of (

    Notes:
        The prefix qaid2_ denotes a mapping where keys are query-annotation-id

    vsmany/vsone counts here. also this is where the filter
    weights and thershold are applied to the matches. Essientally
    nearest neighbors are converted into weighted assignments
    """

    # Config
    K = qreq_.qparams.K
    is_vsone =  qreq_.qparams.vsone
    if NOT_QUIET:
        query_type = qreq_.qparams.query_type
        print('[hs] Step 4) Building chipmatches %s' % (query_type,))
    # Return var
    qaid2_chipmatch = {}
    nFeatMatches = 0
    #Vsone
    if is_vsone:
        assert len(qreq_.get_external_qaids()) == 1
        aid2_fm, aid2_fs, aid2_fk = new_fmfsfk()
    # Iterate over chips with nearest neighbors
    mark_, end_ = log_progress('Build Chipmatch: ', len(qaid2_nns))
    for count, qaid in enumerate(six.iterkeys(qaid2_nns)):
        mark_(count)  # Mark progress
        (qfx2_idx, _) = qaid2_nns[qaid]
        (qfx2_fs, qfx2_valid) = qaid2_nnfilt[qaid]
        nQKpts = qfx2_idx.shape[0]
        # Build feature matches
        qfx2_nnidx = qfx2_idx[:, 0:K]
        qfx2_aid  = qreq_.indexer.get_nn_aids(qfx2_nnidx)
        qfx2_fx   = qreq_.indexer.get_nn_featxs(qfx2_nnidx)
        qfx2_qfx = np.tile(np.arange(nQKpts), (K, 1)).T
        qfx2_k   = np.tile(np.arange(K), (nQKpts, 1))
        # Pack valid feature matches into an interator
        valid_lists = (qfx2[qfx2_valid] for qfx2 in (qfx2_qfx, qfx2_aid, qfx2_fx, qfx2_fs, qfx2_k,))
        # TODO: Sorting the valid lists by aid might help the speed of this
        # code. Also, consolidating fm, fs, and fk into one vector will reduce
        # the amount of appends.
        match_iter = zip(*valid_lists)
        # Vsmany - Append query feature matches to database aids
        if not is_vsone:
            aid2_fm, aid2_fs, aid2_fk = new_fmfsfk()
            for qfx, aid, fx, fs, fk in match_iter:
                aid2_fm[aid].append((qfx, fx))  # Note the difference
                aid2_fs[aid].append(fs)
                aid2_fk[aid].append(fk)
                nFeatMatches += 1
            chipmatch = _fix_fmfsfk(aid2_fm, aid2_fs, aid2_fk)
            qaid2_chipmatch[qaid] = chipmatch
            #if not QUIET:
            #    nFeats_in_matches = [len(fm) for fm in six.itervalues(aid2_fm)]
            #    print('nFeats_in_matches_stats = ' +
            #          utool.dict_str(utool.mystats(nFeats_in_matches)))
        # Vsone - Append database feature matches to query aids
        else:
            for qfx, aid, fx, fs, fk in match_iter:
                aid2_fm[qaid].append((fx, qfx))  # Note the difference
                aid2_fs[qaid].append(fs)
                aid2_fk[qaid].append(fk)
                nFeatMatches += 1
    #Vsone
    if is_vsone:
        chipmatch = _fix_fmfsfk(aid2_fm, aid2_fs, aid2_fk)
        qaid = qreq_.get_external_qaids()[0]
        qaid2_chipmatch[qaid] = chipmatch
    end_()
    if NOT_QUIET:
        print('[hs] * made %d feat matches' % nFeatMatches)
    return qaid2_chipmatch


#============================
# 5) Spatial Verification
#============================


def spatial_verification(qaid2_chipmatch, qreq_, dbginfo=False):
    if not qreq_.qparams.sv_on or qreq_.qparams.xy_thresh is None:
        print('[hs] Step 5) Spatial verification: off')
        return (qaid2_chipmatch, {}) if dbginfo else qaid2_chipmatch
    else:
        return _spatial_verification(qaid2_chipmatch, qreq_, dbginfo=dbginfo)


@profile
def _spatial_verification(qaid2_chipmatch, qreq_, dbginfo=False):
    """ """
    # spatial verification
    print('[hs] Step 5) Spatial verification: ' + qreq_.qparams.sv_cfgstr)
    prescore_method = qreq_.qparams.prescore_method
    nShortlist      = qreq_.qparams.nShortlist
    xy_thresh       = qreq_.qparams.xy_thresh
    scale_thresh    = qreq_.qparams.scale_thresh
    ori_thresh      = qreq_.qparams.ori_thresh
    use_chip_extent = qreq_.qparams.use_chip_extent
    min_nInliers    = qreq_.qparams.min_nInliers
    qaid2_chipmatchSV = {}
    nFeatSVTotal = 0
    nFeatMatchSV = 0
    nFeatMatchSVAff = 0
    if dbginfo:
        qaid2_svtups = {}  # dbg info (can remove if there is a speed issue)
    def print_(msg, count=0):
        """ temp print_. Using count in this way is a hack """
        if NOT_QUIET:
            if count % 25 == 0:
                sys.stdout.write(msg)
            count += 1
    # Find a transform from chip2 to chip1 (the old way was 1 to 2)
    for qaid in six.iterkeys(qaid2_chipmatch):
        chipmatch = qaid2_chipmatch[qaid]
        aid2_prescore = score_chipmatch(qaid, chipmatch, prescore_method, qreq_)
        #print('Prescore: %r' % (aid2_prescore,))
        (aid2_fm, aid2_fs, aid2_fk) = chipmatch
        topx2_aid = utool.util_dict.keys_sorted_by_value(aid2_prescore)[::-1]
        nRerank = min(len(topx2_aid), nShortlist)
        # Precompute output container
        if dbginfo:
            aid2_svtup = {}  # dbg info (can remove if there is a speed issue)
        aid2_fm_V, aid2_fs_V, aid2_fk_V = new_fmfsfk()
        # Query Keypoints
        kpts1 = qreq_.get_annot_kpts(qaid)
        topx2_kpts = qreq_.get_annot_kpts(topx2_aid)
        # Check the diaglen sizes before doing the homography
        topx2_dlen_sqrd = _precompute_topx2_dlen_sqrd(qreq_, aid2_fm, topx2_aid,
                                                      topx2_kpts, nRerank,
                                                      use_chip_extent)
        # spatially verify the top __NUM_RERANK__ results
        for topx in range(nRerank):
            aid = topx2_aid[topx]
            fm = aid2_fm[aid]
            dlen_sqrd = topx2_dlen_sqrd[topx]
            kpts2 = topx2_kpts[topx]
            fs    = aid2_fs[aid]
            fk    = aid2_fk[aid]
            sv_tup = sver.spatial_verification(kpts1, kpts2, fm,
                                               xy_thresh, scale_thresh, ori_thresh, dlen_sqrd,
                                               min_nInliers)
            nFeatSVTotal += len(fm)
            if sv_tup is None:
                    print_('o')  # sv failure
            else:
                # Return the inliers to the homography
                homog_inliers, H, aff_inliers, Aff = sv_tup
                if dbginfo:
                    aid2_svtup[aid] = sv_tup
                aid2_fm_V[aid] = fm[homog_inliers, :]
                aid2_fs_V[aid] = fs[homog_inliers]
                aid2_fk_V[aid] = fk[homog_inliers]
                nFeatMatchSV += len(homog_inliers)
                nFeatMatchSVAff += len(aff_inliers)
                if NOT_QUIET:
                    #print(inliers)
                    print_('.')  # verified something
        # Rebuild the feature match / score arrays to be consistent
        chipmatchSV = _fix_fmfsfk(aid2_fm_V, aid2_fs_V, aid2_fk_V)
        if dbginfo:
            qaid2_svtups[qaid] = aid2_svtup
        qaid2_chipmatchSV[qaid] = chipmatchSV
    print_('\n')
    if NOT_QUIET:
        print('[hs] * Affine verified %d/%d feat matches' % (nFeatMatchSVAff, nFeatSVTotal))
        print('[hs] * Homog  verified %d/%d feat matches' % (nFeatMatchSV, nFeatSVTotal))
    if dbginfo:
        return qaid2_chipmatchSV, qaid2_svtups
    else:
        return qaid2_chipmatchSV


def _precompute_topx2_dlen_sqrd(qreq_, aid2_fm, topx2_aid, topx2_kpts,
                                nRerank, use_chip_extent):
    """ helper for spatial verification, computes the squared diagonal length of
    matching chips """
    if use_chip_extent:
        topx2_chipsize = list(qreq_.get_annot_chipsizes(topx2_aid))
        def chip_dlen_sqrd(tx):
            (chipw, chiph) = topx2_chipsize[tx]
            dlen_sqrd = chipw ** 2 + chiph ** 2
            return dlen_sqrd
        topx2_dlen_sqrd = [chip_dlen_sqrd(tx) for tx in range(nRerank)]
    else:
        # Use extent of matching keypoints
        def kpts_dlen_sqrd(tx):
            kpts2 = topx2_kpts[tx]
            aid = topx2_aid[tx]
            fm  = aid2_fm[aid]
            x_m, y_m = ktool.get_xys(kpts2[fm[:, 1]])
            dlensqrd = (x_m.max() - x_m.min()) ** 2 + (y_m.max() - y_m.min()) ** 2
            return dlensqrd
        topx2_dlen_sqrd = [kpts_dlen_sqrd(tx) for tx in range(nRerank)]
    return topx2_dlen_sqrd


#============================
# Scoring Mechanism
#============================

@profile
def score_chipmatch(qaid, chipmatch, score_method, qreq_):
    (aid2_fm, aid2_fs, aid2_fk) = chipmatch
    # HACK: Im not even sure if the 'w' suffix is correctly handled anymore
    if score_method.find('w') == len(score_method) - 1:
        score_method = score_method[:-1]
    # Choose the appropriate scoring mechanism
    if score_method == 'csum':
        aid2_score = vr2.score_chipmatch_csum(chipmatch)
    #elif score_method == 'pl':
    #    aid2_score, nid2_score = vr2.score_chipmatch_PL(qaid, chipmatch, qreq_)
    #elif score_method == 'borda':
    #    aid2_score, nid2_score = vr2.score_chipmatch_pos(qaid, chipmatch, qreq_, 'borda')
    #elif score_method == 'topk':
    #    aid2_score, nid2_score = vr2.score_chipmatch_pos(qaid, chipmatch, qreq_, 'topk')
    #elif score_method.startswith('coverage'):
    #    # Method num is at the end of coverage
    #    method = int(score_method.replace('coverage', '0'))
    #    aid2_score = coverage_image.score_chipmatch_coverage(qaid, chipmatch, qreq_, method=method)
    else:
        raise Exception('[hs] unknown scoring method:' + score_method)
    return aid2_score


#============================
# 6) Query Result Format
#============================


@profile
def chipmatch_to_resdict(qaid2_chipmatch, filt2_meta, qreq_,
                         qaid2_scores=None):
    if NOT_QUIET:
        print('[hs] Step 6) Convert chipmatch -> qres')
    qaids   = qreq_.get_external_qaids()
    qauuids = qreq_.get_external_quuids()
    cfgstr = qreq_.get_cfgstr()
    score_method = qreq_.qparams.score_method
    # Create the result structures for each query.
    qaid2_qres = {}
    # Currently not looping over the keys so we have access to uuids
    # using qreq externals aids should be equivalent
    #for qaid in six.iterkeys(qaid2_chipmatch):
    for qaid, qauuid in zip(qaids, qauuids):
        # Create a query result structure
        qres = hots_query_result.QueryResult(qaid, qauuid, cfgstr)
        qaid2_qres[qaid] = qres

    for qaid, qres in six.iteritems(qaid2_qres):
        # For each query's chipmatch
        chipmatch = qaid2_chipmatch[qaid]
        if chipmatch is not None:
            aid2_fm, aid2_fs, aid2_fk = chipmatch
            qres.aid2_fm = aid2_fm
            qres.aid2_fs = aid2_fs
            qres.aid2_fk = aid2_fk

        # Perform final scoring
        if qaid2_scores is None:
            aid2_score = score_chipmatch(qaid, chipmatch, score_method, qreq_)
        else:
            aid2_score = qaid2_scores[qaid]
            if not isinstance(aid2_score, dict):
                # Pandas hack
                aid2_score = aid2_score.to_dict()
        # Populate query result fields
        qres.aid2_score = aid2_score

        qres.filt2_meta = {}  # dbgstats
        for filt, qaid2_meta in six.iteritems(filt2_meta):
            qres.filt2_meta[filt] = qaid2_meta[qaid]  # things like k+1th
    # Retain original score method
    return qaid2_qres


@profile
def try_load_resdict(qreq_, force_miss=False):
    """ Try and load the result structures for each query.
    returns a list of failed qaids """
    qaids   = qreq_.get_external_qaids()
    qauuids = qreq_.get_external_quuids()

    cfgstr = qreq_.get_cfgstr()
    qresdir = qreq_.get_qresdir()
    qaid2_qres_hit = {}
    cachemiss_qaids = []
    for qaid, qauuid in zip(qaids, qauuids):
        try:
            qres = hots_query_result.QueryResult(qaid, qauuid, cfgstr)
            qres.load(qresdir, force_miss=force_miss)  # 77.4 % time
            qaid2_qres_hit[qaid] = qres  # cache hit
        except (hsexcept.HotsCacheMissError, hsexcept.HotsNeedsRecomputeError):
            cachemiss_qaids.append(qaid)  # cache miss
    return qaid2_qres_hit, cachemiss_qaids


def save_resdict(qreq_, qaid2_qres):
    qresdir = qreq_.get_qresdir()
    for qres in six.itervalues(qaid2_qres):
        qres.save(qresdir)
