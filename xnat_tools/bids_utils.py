import json
import os
import logging
import collections
import six
import pydicom
import shutil

from six.moves import zip
from xnat_tools.xnat_utils import get, download
from collections import defaultdict

_logger = logging.getLogger(__name__)


def insert_intended_for_fmap(bids_dir, sub_list):
    """Insert the IntendedFor field to JSON sidecart for fieldmap data"""

    for subj in sub_list:

        # makes list of the json files to edit
        subj_path = f"{bids_dir}/sub-{subj}"
        _logger.info(f"Processing participant {subj} at path {subj_path}")

        subj_sub_dirs = os.listdir(subj_path)
        sess_list = [x for x in subj_sub_dirs if x.startswith("ses-")]
        _logger.info(f"List of sessions sub-directories {sess_list}")

        for sess in sess_list:

            fmap_path = f"{bids_dir}/sub-{subj}/{sess}/fmap"
            func_path = f"{bids_dir}/sub-{subj}/{sess}/func"
            fmap_files = [os.path.join(fmap_path, f) for f in os.listdir(fmap_path)]
            json_files = [f for f in fmap_files if f.endswith(".json")]
            _logger.info(f"List of JSON files to amend {json_files}")

            # makes list of the func files to add into the intended for field
            func_files = [f"{sess}/func/{file}" for file in os.listdir(func_path)]
            nii_files = [i for i in func_files if i.endswith(".nii.gz")]
            _logger.info(f"List of NII files")

            # Open the json files ('r' for read only) as a dictionary
            # Adds the Intended for key
            # Add the func files to the key value
            # The f.close is a duplication.
            # f can only be used inside the with "loop"
            # we open the file again to write only and
            # dump the dictionary to the files
            for file in json_files:
                os.chmod(file, 0o664)
                with open(file, "r") as f:
                    _logger.info(f"Processing file {f}")
                    data = json.load(f)
                    data["IntendedFor"] = nii_files
                    f.close
                with open(file, "w") as f:
                    json.dump(data, f, indent=4, sort_keys=True)
                    f.close
                    _logger.info("Done with re-write")


def prepare_bids_prefixes(project, subject, session):
    # get PI from project name
    pi_prefix = project.lower().split("_")[0]

    # Paths to export source data in a BIDS friendly way
    study_prefix = "study-" + project.lower().split("_")[1]
    subject_prefix = "sub-" + subject.lower().replace("_", "")
    session_prefix = "ses-" + session.lower().replace("_", "")

    return pi_prefix, study_prefix, subject_prefix, session_prefix


def prepare_export_output_path(
    bids_root_dir,
    pi_prefix,
    study_prefix,
    subject_prefix,
    session_prefix,
    overwrite=False,
):

    study_dir = os.path.join(bids_root_dir, pi_prefix, study_prefix)
    subject_dir = os.path.join(study_dir, "xnat-export", subject_prefix)
    session_dir = os.path.join(subject_dir, session_prefix)

    # Set up working directory
    if overwrite and os.path.exists(session_dir):
        _logger.info("Removing existing xnat-export session directory %s" % session_dir)
        shutil.rmtree(session_dir, ignore_errors=True)

    if not os.path.isdir(session_dir):
        _logger.info("Making output xnat-export session directory %s" % session_dir)
        os.makedirs(session_dir)

    return session_dir


def prepare_heudi_prefixes(project, subject, session):
    # get PI from project name
    pi_prefix = project.lower().split("_")[0]

    # Paths to export source data in a BIDS friendly way
    study_prefix = "study-" + project.lower().split("_")[1]
    subject_prefix = "sub-" + subject.lower().replace("_", "")
    session_prefix = "ses-" + session.lower().replace("_", "")

    return pi_prefix, study_prefix, subject_prefix, session_prefix


def prepare_heudiconv_output_path(
    bids_root_dir,
    pi_prefix,
    study_prefix,
    subject_prefix,
    session_prefix,
    overwrite=False,
):

    heudi_study_dir = os.path.join(bids_root_dir, pi_prefix, study_prefix)
    heudi_output_dir = os.path.join(heudi_study_dir, "bids")
    subject_dir = os.path.join(heudi_output_dir, subject_prefix)
    session_dir = os.path.join(subject_dir, session_prefix)

    # Set up working directory
    if overwrite:
        print("Overwrite - Removing existing heudi session directory %s" % session_dir)
        shutil.rmtree(session_dir, ignore_errors=True)

    if not os.path.isdir(heudi_output_dir):
        print("Making output BIDS Session directory %s" % heudi_output_dir)
        os.makedirs(heudi_output_dir)

    return heudi_output_dir


def bidsmap_scans(scans, bidsmap=None):
    """Filter the series descriptions based on the bidsmap file"""
    # NOTE (BNR): We could break these down into smaller functions, one for
    #             bidsmap, one for scanner exceptions, one for run+, but that
    #             would add an extra loop per function. I feel like this
    #             strikes a balance. One loop to handle the scan_id stuff, one
    #             loop to handle the series_description stuff.

    if bidsmap is None:
        bidsmap = []

    # NOTE (BNR): First thing we do is flatten the bidsmap structure. This makes
    #             the bidsmap much easier to use when trying to figure out which
    #             sequences match something in the bidsmap file.
    bidsmap = {i["series_description"]: i["bidsname"] for i in bidsmap}

    # NOTE (BNR): In order to replace run+ we need to keep a count of how many
    #             times we've seen a particular series_description before. That
    #             is where the defaultdict comes in. It helps us keep track of
    #             the series_descriptions we've seen before.
    run_count_cache = defaultdict(int)

    desired_scans = []
    for scan_id, series_description in scans:
        if series_description in bidsmap:
            series_description = bidsmap[series_description]

        series_description = handle_scanner_exceptions(series_description)

        if "run+" in series_description:
            run_count_cache[series_description] += 1
            series_description = series_description.replace(
                "run+", f"run-{run_count_cache[series_description]:02}"
            )

        desired_scans.append((scan_id, series_description))

    return desired_scans


def handle_scanner_exceptions(match):
    # T1W and T2W need to be upper case
    match = match.replace("t1w", "T1w")
    match = match.replace("t2w", "T2w")

    # Handle the aascout planes
    match = match.replace("_MPR_sag", "MPRsag")
    match = match.replace("_MPR_cor", "MPRcor")
    match = match.replace("_MPR_tra", "MPRtra")

    # Handle the mprage rms
    match = match.replace(" RMS", "RMS")

    return match


def bidsify_dicom_headers(filename, series_description):
    """Updates the DICOM headers to match the new series_description"""

    dataset = pydicom.dcmread(filename)

    if "ProtocolName" not in dataset:
        return

    if dataset.data_element("ProtocolName").value != series_description:
        dataset.data_element("ProtocolName").value = series_description
        dataset.data_element("SeriesDescription").value = series_description


def scan_contains_dicom(connection, host, session, scanid):
    """Checks to see if the scan has suitable DICOM files for BIDS conversion"""
    resp = get(
        connection,
        host + "/data/experiments/%s/scans/%s/resources" % (session, scanid),
        params={"format": "json"},
    )

    dicomResourceList = [
        r for r in resp.json()["ResultSet"]["Result"] if r["label"] == "DICOM"
    ]

    # NOTE (BNR): A scan contains multiple resources. A resource can be thought
    #             of as a folder. We only want a single DICOM folder. If we have
    #             multiple, something is weird. If we don't have any DICOM
    #             resources the scan doesn't have any DICOM images. We only
    #             download the scan if there's a single DICOM resource
    if len(dicomResourceList) <= 0:
        return False
    elif len(dicomResourceList) > 1:
        return False
    else:
        dicomResource = dicomResourceList[0]

    # NOTE (BNR): We only want to process the scan if we have dicom files. But
    #       sometimes the file_count field is empty and we process anyway even
    #       though that might make things break later
    if dicomResource.get("file_count") is None:
        _logger.warning(
            'DICOM resources for scan %s have a blank "file_count". '
            "I cannot check to see if there are no files. "
            "I am not skipping the scan. "
            "This may lead to errors later if there are no DICOM files in the scan.",
            scanid,
        )
        return True
    elif int(dicomResource["file_count"]) == 0:
        return False

    return True


def assign_bids_name(
    connection, host, subject, session, scans, build_dir, bids_session_dir,
):
    """
        subject: Subject to process
        scans: Tuple of scan id and series descriptions
        build_dir: build director. What is this?
        study_bids_dir: BIDS directory to copy simlinks to. Typically the RESOURCES/BIDS
    """

    for scanid, seriesdesc in scans:
        if not scan_contains_dicom(connection, host, session, scanid):
            continue


        # BIDS sourcedatadirectory for this scan
        _logger.info(f"bids_session_dir: {bids_session_dir}")
        _logger.info(f"BIDSNAME: {seriesdesc}")
        bids_scan_directory = os.path.join(bids_session_dir, seriesdesc)

        if not os.path.isdir(bids_scan_directory):
            _logger.info("Making scan DICOM directory %s." % bids_scan_directory)
            os.mkdir(bids_scan_directory)
        else:
            _logger.warning(
                f"{bids_scan_directory} already exists. See documentation to understad how xnat_tools handles repeated sequences."
            )

        filesURL = host + "/data/experiments/%s/scans/%s/resources/DICOM/files" % (
            session,
            scanid,
        )

        r = get(connection, filesURL, params={"format": "json"})
        # Build a dict keyed off file name
        dicomFileDict = {
            dicom["Name"]: {"URI": host + dicom["URI"]}
            for dicom in r.json()["ResultSet"]["Result"]
        }

        # Have to manually add absolutePath with a separate request
        r = get(
            connection, filesURL, params={"format": "json", "locator": "absolutePath"}
        )
        for dicom in r.json()["ResultSet"]["Result"]:
            dicomFileDict[dicom["Name"]]["absolutePath"] = dicom["absolutePath"]

        # Download DICOMs
        _logger.info("Downloading files")
        os.chdir(bids_scan_directory)
        dicomFileList = list(dicomFileDict.items())
        (name, pathDict) = dicomFileList[0]
        download(connection, name, pathDict)

        bidsify_dicom_headers(name, seriesdesc)

        # Download remaining DICOMs
        for name, pathDict in dicomFileList[1:]:
            download(connection, name, pathDict)
            bidsify_dicom_headers(name, seriesdesc)

        os.chdir(build_dir)
        _logger.info("Done.")
        _logger.info("---------------------------------")
