import json
import logging
import os
import shutil
import warnings
from collections import defaultdict

import pydicom

from xnat_tools.xnat_utils import download, get

_logger = logging.getLogger(__name__)


def insert_intended_for_fmap(
    bids_dir,
    sub_list,
    session="",
    sess_list=[],
    overwrite=False,
):
    """Insert the IntendedFor field to JSON sidecart for fieldmap data"""

    for subj in sub_list:

        # makes list of the json files to edit
        subj_path = f"{bids_dir}/sub-{subj}"
        _logger.info(f"Processing participant {subj} at path {subj_path}")

        subj_sub_dirs = os.listdir(subj_path)

        # If a session is provided, only process that session.
        # If the includesess list is not empty, cocatenate all session
        # suffixes with "ses-" prefix for the file path.
        # Otherwise, include all sessions for every subject to be processed.
        if session != "":
            sessions = ["ses-" + session]
        elif sess_list != []:
            sessions = ["ses-" + x for x in sess_list]
        else:
            sessions = [x for x in subj_sub_dirs if x.startswith("ses-")]

        _logger.info(f"List of sessions sub-directories {sess_list}")

        for sess in sessions:

            fmap_path = f"{bids_dir}/sub-{subj}/{sess}/fmap"
            func_path = f"{bids_dir}/sub-{subj}/{sess}/func"
            dwi_path = f"{bids_dir}/sub-{subj}/{sess}/dwi"

            # Initialize boolean variables for fmapExists, funcExists, and diffExists
            fmapPathExists = os.path.exists(fmap_path)
            funcPathExists = os.path.exists(func_path)
            diffPathExists = os.path.exists(dwi_path)

            # Don't do anything if this session doesn't contain a fieldmap folder
            if not fmapPathExists:
                continue

            # Separate fmaps into distinct geometries
            fmap_files = [
                os.path.join(fmap_path, f) for f in os.listdir(fmap_path) if f.endswith("json")
            ]

            bold_fmap_files = [
                f
                for f in fmap_files
                if get_acquisition_tag(f.split("_")).__contains__("bold") and f.endswith(".json")
            ]

            fmap_bold_acq_files = {get_acquisition_tag(f.split("_")) for f in bold_fmap_files}

            diff_fmap_files = [
                f
                for f in fmap_files
                if get_acquisition_tag(f.split("_")).__contains__("diff") and f.endswith(".json")
            ]

            fmap_diff_acq_files = {get_acquisition_tag(f.split("_")) for f in diff_fmap_files}

            # Log JSON file lists
            _logger.info(f"List of BOLD JSON files to amend {bold_fmap_files}")
            _logger.info(f"List of DIFF JSON files to amend {diff_fmap_files}")

            # Assemble list of the functional files to add into the intended for field
            if funcPathExists:
                func_files = [f"{sess}/func/{file}" for file in os.listdir(func_path)]
                nii_func_files = [i for i in func_files if i.endswith(".nii.gz")]
                _logger.info(f"List of func NII files {nii_func_files}")
                # If there is one field map, with one list of scans, assume correlation and insert.
                if len(fmap_bold_acq_files) == 1:
                    for fmap in bold_fmap_files:
                        insert_intendedfor_scans(fmap, nii_func_files, overwrite)
                else:
                    process_fmap_json_files(bold_fmap_files, nii_func_files, overwrite)

            # Assemble list of the diffusion files to add into the intended for field
            if diffPathExists:
                dwi_files = [f"{sess}/dwi/{file}" for file in os.listdir(dwi_path)]
                nii_dwi_files = [i for i in dwi_files if i.endswith(".nii.gz")]
                _logger.info(f"List of diff NII files {nii_dwi_files}")
                # If there is one field map, with one list of scans, assume correlation and insert.
                if len(fmap_diff_acq_files) == 1:
                    for fmap in diff_fmap_files:
                        insert_intendedfor_scans(fmap, nii_dwi_files, overwrite)
                else:
                    process_fmap_json_files(diff_fmap_files, nii_dwi_files, overwrite)


# Extract aquisition token from filename
def get_acquisition_tag(bids_tokens: list):
    for token in bids_tokens:
        if token.__contains__("acq"):
            return token
    return ""


# Insert IntendedFor attribute into json fieldmap file.
def insert_intendedfor_scans(fmap: str, nii_files: list, overwrite: bool):
    # Open the json files ('r' for read only) as a dictionary
    # Adds the Intended for key if IntendeFor does not exist
    # as a property. Then, add the func files to the key value
    #
    # The f.close is a duplication.
    # f can only be used inside the with "loop"
    # we open the file again to write only and
    # dump the dictionary to the files
    os.chmod(fmap, 0o664)
    with open(fmap, "r") as rf:
        _logger.info(f"Processing file {rf}")
        data = json.load(rf)
        if "IntendedFor" not in data or overwrite:
            data["IntendedFor"] = nii_files
            with open(fmap, "w") as wf:
                json.dump(data, wf, indent=4, sort_keys=True)
                wf.close
            _logger.info("Done with re-write")
        rf.close


def process_fmap_json_files(fmap_files: list, nii_files: list, overwrite: bool):
    # Validates matching acquisition tags before adding
    # to field map's IntendedFor attribute. If there exists
    # multiplate scans with varying acquisition tags, log
    # a warning for the user and stop file processing.
    if len(fmap_files):
        if check_fmap_acquistion_tags(fmap_files):
            for fmap in fmap_files:
                insert_intendedfor_scans(fmap, nii_files, overwrite)


# Verify all acquisition tags of a given list match.
def check_fmap_acquistion_tags(fieldmaps: list):
    for fmap in fieldmaps:
        acq_tag = get_acquisition_tag(fieldmaps[0].split("_"))
        if acq_tag != get_acquisition_tag(fmap.split("_")):
            _logger.warning(
                "Multiple Field Maps With Diferring Acquisition Tags."
                "Resolve FMAP IntendedFor Ambiguities."
            )

            return False
    return True


def path_string_preprocess(proj: str, subj: str, sess: str):
    """Preprocess study, session and subject strings"""

    proj = proj.lower()
    subj = subj.lower().replace("_", "").replace("-", "")
    sess = sess.lower().replace("_", "").replace("-", "")

    return proj, subj, sess


def prepare_path_prefixes(project, subject, session):
    # get PI from project name
    pi_prefix = project.split("_")[0]

    # Paths to export source data in a BIDS friendly way
    study_prefix = "study-" + project.split("_")[1]
    subject_prefix = "sub-" + subject
    session_prefix = "ses-" + session

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
        shutil.rmtree(session_dir, ignore_errors=False)

    if not os.path.isdir(session_dir):
        _logger.info("Making output xnat-export session directory %s" % session_dir)
        os.makedirs(session_dir, exist_ok=True)

    return session_dir


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
        print("Overwrite - Removing heudi session directory %s" % session_dir)
        shutil.rmtree(session_dir, ignore_errors=True)
        if os.path.isdir(session_dir):
            warnings.warn(f"Something went wrong: {session_dir} was not removed")

        heudi_source_dir = os.path.join(heudi_study_dir, "bids/sourcedata")
        source_subject_dir = os.path.join(heudi_source_dir, subject_prefix)
        source_session_dir = os.path.join(source_subject_dir, session_prefix)
        print("Overwrite - Removing sourcedata session directory %s" % source_session_dir)
        shutil.rmtree(source_session_dir, ignore_errors=True)
        if os.path.isdir(source_session_dir):
            warnings.warn(f"Something went wrong: {source_session_dir} was not removed")

        heudi_hidden_dir = os.path.join(heudi_study_dir, "bids/.heudiconv")
        hidden_subject_dir = os.path.join(heudi_hidden_dir, subject_prefix.split("-")[1])
        hidden_session_dir = os.path.join(hidden_subject_dir, session_prefix)
        print("Overwrite - Removing hidden session directory %s" % hidden_session_dir)
        shutil.rmtree(hidden_session_dir, ignore_errors=True)
        if os.path.isdir(hidden_session_dir):
            warnings.warn(f"Something went wrong: {hidden_session_dir} was not removed")

    if not os.path.isdir(heudi_output_dir):
        print("Making output BIDS Session directory %s" % heudi_output_dir)
        os.makedirs(heudi_output_dir, exist_ok=True)

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

    # Handle diffusion derivatives
    match = match.replace("_TENSOR", "TENSOR")

    return match


def bidsify_dicom_headers(filename, series_description):
    """Updates the DICOM headers to match the new series_description"""

    dataset = pydicom.dcmread(filename)

    protocol_header = dataset.data_element("ProtocolName").value
    seriesdesc_header = dataset.data_element("SeriesDescription").value
    if protocol_header != series_description:
        warnings.warn(
            f"Changed DICOM HEADER[ProtocolName and SeriesDescription]: \
            {protocol_header} -> {series_description} \
            {seriesdesc_header} -> {series_description}"
        )
        # Heudiconv appends derivative tag for SBRef, which is already present
        # within series_description. To avoid redundant derivative tagging
        # for SBRef, skip assigning series_description to DICOM ProtocolName.
        if series_description.__contains__("SBRef"):
            dataset.data_element("ProtocolName").value = series_description.replace("_SBRef", "")
            dataset.data_element("SeriesDescription").value = series_description
        else:
            dataset.data_element("ProtocolName").value = series_description
            dataset.data_element("SeriesDescription").value = series_description

        dataset.save_as(filename)


def scan_contains_dicom(connection, host, session, scanid):
    """Checks to see if the scan has suitable DICOM files for BIDS conversion"""
    resp = get(
        connection,
        host + "/data/experiments/%s/scans/%s/resources" % (session, scanid),
        params={"format": "json"},
    )

    dicomResourceList = [r for r in resp.json()["ResultSet"]["Result"] if r["format"] == "DICOM"]
    _logger.debug(f"Found DICOM resources: {dicomResourceList}")
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
    connection,
    host,
    subject,
    session,
    scans,
    build_dir,
    bids_session_dir,
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
                f"{bids_scan_directory} already exists. \
                See documentation to understand behavior for repeated sequences."
            )

        # check the label to figure out which folder xnat has the dicoms stored
        # in (DICOMS or secondary)
        resourcesURL = host + f"/data/experiments/{session}/scans/{scanid}/resources/"

        resp = get(
            connection,
            resourcesURL,
            params={"format": "json"},
        )

        # limit the resources to ones that are DICOM format
        dicomResourceList = [
            r for r in resp.json()["ResultSet"]["Result"] if r["format"] == "DICOM"
        ]

        # check the label of our one DICOM resource
        resourceLabel = dicomResourceList[0]["label"]
        _logger.debug(f"resource label: {resourceLabel}")

        # the DICOM file path is determined by the "label" xnat has applied to that
        # resource
        filesURL = resourcesURL + "%s/files" % (resourceLabel,)

        r = get(connection, filesURL, params={"format": "json"})
        # Build a dict keyed off file name
        dicomFileDict = {
            dicom["Name"]: {"URI": host + dicom["URI"]} for dicom in r.json()["ResultSet"]["Result"]
        }

        # Have to manually add absolutePath with a separate request
        r = get(connection, filesURL, params={"format": "json", "locator": "absolutePath"})
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
