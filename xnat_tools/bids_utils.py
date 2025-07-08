import glob
import json
import logging
import os
import shutil
import subprocess
import warnings
from collections import defaultdict

import pydicom
from heudiconv.bids import add_rows_to_scans_keys_file, get_formatted_scans_key_row
from mne.io import read_raw_brainvision
from mne_bids import BIDSPath, write_raw_bids

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

        sessions = build_sessions_list(bids_dir, subj, session, sess_list)

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
                _logger.info(f"List of func .nii files {nii_func_files}")
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
                _logger.info(f"List of diff .nii files {nii_dwi_files}")
                # If there is one field map, with one list of scans, assume correlation and insert.
                if len(fmap_diff_acq_files) == 1:
                    for fmap in diff_fmap_files:
                        insert_intendedfor_scans(fmap, nii_dwi_files, overwrite)
                else:
                    process_fmap_json_files(diff_fmap_files, nii_dwi_files, overwrite)


def build_sessions_list(bids_dir, subj, session="", sess_list=None):
    subj_path = f"{bids_dir}/sub-{subj}"
    subj_sub_dirs = os.listdir(subj_path)

    log_info(f"Processing participant {subj} at path {subj_path}")

    # If a session is provided, only process that session.
    # If the includesess list is not empty, cocatenate all session
    # suffixes with "ses-" prefix for the file path.
    # Otherwise, include all sessions for this subject
    if session != "":
        sessions = ["ses-" + session]
    elif sess_list is not None:
        sessions = ["ses-" + x for x in sess_list]
    else:
        sessions = [x for x in subj_sub_dirs if x.startswith("ses-")]

    return sessions


def ensure_json_field(json_path, field, default):
    """Add 'Units' key with empty value if missing from JSON."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if field not in data:
            data[field] = default

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            _logger.info(f"Added {field} field to {json_path}")
        else:
            _logger.info(f"{field} field already present in {json_path}")
    except Exception as e:
        _logger.info(f"Error processing {json_path}: {e}")


def append_anat_units_field(bids_dir, sub_list=None, session="", sess_list=None):
    anat_dirs = [
        f"{bids_dir}/sub-{subj}/ses-{sess}/anat" for subj in sub_list for sess in sess_list
    ]

    for dir in anat_dirs:
        anat_jsons = [os.path.join(dir, f) for f in os.listdir(dir) if f.endswith("json")]

        for path in anat_jsons:
            # Phase images (with the `part-phase` entity) must have units "rad" or "arbitrary".
            ensure_json_field(path, "Units", "arbitrary")


def remove_func_acquisition_duration_field(bids_dir, sub_list=None, session="", sess_list=None):
    """Remove AcquisitionDuration from func jsons if RepetitionTime is defined"""

    for subj in sub_list:
        # makes list of the json files to edit

        sessions = build_sessions_list(bids_dir, subj, session, sess_list)

        _logger.info(f"List of sessions sub-directories {sessions}")

        for sess in sessions:
            func_path = f"{bids_dir}/sub-{subj}/{sess}/func"

            # Don't do anything if this session doesn't contain a func folder
            if not os.path.exists(func_path):
                continue

            func_jsons = [
                os.path.join(func_path, f) for f in os.listdir(func_path) if f.endswith("json")
            ]

            task_bold_jsons = glob.glob(os.path.join(bids_dir, "task*_bold.json"))

            func_jsons = func_jsons + task_bold_jsons

            # Log JSON file lists
            _logger.info(f"List of BOLD JSON files to amend {func_jsons}")

            for js in func_jsons:
                os.chmod(js, 0o664)
                with open(js, "r") as rj:
                    log_info(f"\nProcessing file {rj.name}")
                    data = json.load(rj)
                    if all(key in data for key in ("AcquisitionDuration", "RepetitionTime")):
                        del data["AcquisitionDuration"]
                        log_info(
                            ">> AcquisitionDuration and RepetitionTime are mutually "
                            "exclusive for BOLD data according to the BIDS spec. "
                            "Removing AcquisitionDuration field."
                        )
                        with open(js, "w") as wj:
                            json.dump(data, wj, indent=4, sort_keys=True)
                            wj.close()
                    else:
                        log_info(">> No modification needed.")
                    rj.close()


def correct_for_bids_schema_validator(bids_dir, sub_list=None, session="", sess_list=None):
    if sub_list is None:
        sub_list = [x.removeprefix("sub-") for x in os.listdir(bids_dir) if x.startswith("sub-")]

    remove_func_acquisition_duration_field(bids_dir, sub_list, session, sess_list)
    append_anat_units_field(bids_dir, sub_list, session, sess_list)


# Extract aquisition token from filename
def get_acquisition_tag(bids_tokens: list):
    for token in bids_tokens:
        if token.__contains__("acq"):
            return token
    return ""


# switch to print statements if we don't have logger (i.e. run from CLI)
def log_info(msg):
    if _logger and _logger.hasHandlers():
        _logger.info(msg)
    else:
        print(msg)


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
        _logger.info(f"Processing file {rf.name}")
        data = json.load(rf)
        if "IntendedFor" not in data or overwrite:
            data["IntendedFor"] = nii_files
            with open(fmap, "w") as wf:
                json.dump(data, wf, indent=4, sort_keys=True)
                wf.close()
            _logger.info("Done with re-write")
        rf.close()


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


def add_magphase_part_entity(allscans, filename, series_description):
    # heudiconv/reproin do this automatically if magnitude and phase
    # data are included in a single series, but we have to do it manually
    # if the scanner exports them in separate series

    # find all scan names, excluding any fieldmaps
    scannames = []
    for s in allscans:
        if "fmap_" not in s[1]:
            scannames.append(s[1])
    # look for any duplicated series descriptions with exactly two duplicates
    duplicates = [item for item in set(scannames) if scannames.count(item) == 2]

    # append _part-mag or part-phase if the image type field in the DICOM indicates
    # that datatype
    if series_description in duplicates:
        dup_dataset = pydicom.dcmread(filename)
        if "P" in dup_dataset.data_element("ImageType").value:
            series_description = series_description + "_part-phase"
        elif "M" in dup_dataset.data_element("ImageType").value:
            series_description = series_description + "_part-mag"

    return series_description


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


def download_resources(connection, host, session, bids_session_dir):
    r = get(
        connection,
        f"{host}/data/experiments/{session}/files",
        params={"format": "json"},
    )

    # Build dictionary of format { filename: (pathURI, collectionType) } for every resource
    resourceFileDict = {
        resource["Name"]: ({"URI": host + resource["URI"]}, resource["collection"])
        for resource in r.json()["ResultSet"]["Result"]
    }

    resourceFileList = list(resourceFileDict.items())

    build_dir = os.getcwd()
    # Download Resources
    for name, resourceDetails in resourceFileList:
        _logger.info(f"Downloading files: {name}")
        pathURI = resourceDetails[0]
        collection = resourceDetails[1]
        bids_scan_directory = os.path.join(bids_session_dir, collection)
        if not (os.path.isdir(bids_scan_directory)):
            os.mkdir(bids_scan_directory)

        os.chdir(bids_scan_directory)
        download(connection, name, pathURI)
        os.chdir(build_dir)


# Function to sort by frame acquisition number in dicom filename
def extract_slice_number(filename: str) -> int:
    parts = filename.split("-")

    if len(parts) > 2:
        numeric_part = parts[-2]
        return int(numeric_part)

    return 0


# Load enhanced dicom header.
def read_dicom_header(file_path: str):
    dicom = pydicom.dcmread(file_path, stop_before_pixels=True)
    return dicom


def validate_frame_counts(scans: list, bids_session_dir: str) -> None:

    for _, series_desc in scans:
        if "func" in series_desc:
            bids_scan_dir = os.path.join(bids_session_dir, series_desc)

            with os.scandir(bids_scan_dir) as entries:
                dicom_files = sorted(
                    [
                        entry.name
                        for entry in entries
                        if entry.is_file() and entry.name.endswith(".dcm")
                    ],
                    key=extract_slice_number,
                )

            # Compare frame counts of first and all other DICOMs. Remove other DICOMs if unequal.
            # Should generally only be the last DICOM, unless data is multiecho and/or mag/phase
            if dicom_files:
                volume_temporal_idx = []
                bad_vols = set()

                first_dicom = read_dicom_header(os.path.join(bids_scan_dir, dicom_files[0]))
                # read the DICOM field that reports the number of frames (slices)
                first_frame_count = first_dicom.get((0x0028, 0x0008), None)

                # this grabs the DICOM field that reports the volume number (1-indexed) for the
                # first frame in the volume (and assumes that all frames have the same value)
                volume_temporal_idx.append(
                    first_dicom.PerFrameFunctionalGroupsSequence[0]
                    .FrameContentSequence[0]
                    .TemporalPositionIndex
                )

                for dicomfile in dicom_files[1:]:
                    subsequent_dicom = read_dicom_header(os.path.join(bids_scan_dir, dicomfile))
                    curr_frame_count = subsequent_dicom.get((0x0028, 0x0008), None)
                    curr_temporal_idx = (
                        subsequent_dicom.PerFrameFunctionalGroupsSequence[0]
                        .FrameContentSequence[0]
                        .TemporalPositionIndex
                    )
                    volume_temporal_idx.append(curr_temporal_idx)

                    if curr_frame_count != first_frame_count:
                        bad_vols.add(curr_temporal_idx)

                # any DICOM, regardless of its frame count, that comes from a volume with
                # a partial DICOM needs to be deleted (handles multi-echo data)
                dicoms_to_drop = [
                    dicom_files[i] for i, n in enumerate(volume_temporal_idx) if n in bad_vols
                ]

                for dcmfile in dicoms_to_drop:
                    partial_file_path = os.path.join(bids_scan_dir, dcmfile)

                    if os.path.exists(partial_file_path):
                        _logger.info(
                            f"Detected discrepant frame counts. Removing {partial_file_path}"
                        )
                        os.remove(partial_file_path)


def assign_bids_name(
    connection,
    host,
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
    # Build a dict keyed off file name

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

        seriesdesc = add_magphase_part_entity(scans, name, seriesdesc)
        bidsify_dicom_headers(name, seriesdesc)

        # Download remaining DICOMs
        for name, pathDict in dicomFileList[1:]:
            download(connection, name, pathDict)
            bidsify_dicom_headers(name, seriesdesc)

        os.chdir(build_dir)
        _logger.info("Done.")
        _logger.info("---------------------------------")


def run_mne_eeg2bids(
    subject,
    session_suffix,
    bids_experiment_dir,
    eeg_data_path,
):

    # Find BrainVision header file, extract BIDS key-value pairs from file name
    for file_name in os.listdir(eeg_data_path):
        if file_name.endswith(".vhdr"):
            vhdr_file = os.path.join(eeg_data_path, file_name)
            file_prefix = file_name.split(".")[0]
            bids_keyval_dict = dict(
                keyval.split("-") for keyval in file_prefix.split("_") if "-" in keyval
            )

            params = {}
            # these are the arguments allowed by the BIDSPath function
            possible_bids_keys = dict(
                task="task",
                acq="acquisition",
                run="run",
                proc="processing",
                rec="recording",
                space="space",
                split="split",
                desc="description",
            )
            for k in possible_bids_keys:
                if k in bids_keyval_dict:
                    if k in ["run", "split"]:
                        params[possible_bids_keys[k]] = int(bids_keyval_dict[k])
                    else:
                        params[possible_bids_keys[k]] = bids_keyval_dict[k]

            if "task" not in bids_keyval_dict:
                params["task"] = "todo"

            # Fetch EEG data via MNE's IO function for BrainVision
            raw = read_raw_brainvision(vhdr_file)

            # Allow MNE to construct BIDS Path with available session data
            bids_path = BIDSPath(
                subject=subject,
                session=session_suffix,
                root=f"{bids_experiment_dir}",
                **params,
            )

            # Ouput EEG-BIDS data to defined path
            write_raw_bids(raw, bids_path, overwrite=True)


def correct_dicom_header(export_session_dir, dicomfix_config_path):

    # Check that the configuration file exists
    if not os.path.exists(dicomfix_config_path):
        _logger.warning(
            f"ERROR: The DICOM correction config file '{dicomfix_config_path}' does not exist."
        )
        return

    # Load the configuration file
    with open(dicomfix_config_path, "r") as file:
        try:
            config = json.load(file)
        except json.JSONDecodeError as e:
            _logger.warning(f"Error parsing the configuration file: {e}")
            return

    mappings = config["mappings"]

    for mapping in mappings:
        scans_to_correct = mapping.get("scans_to_correct", [])
        dicom_field = mapping.get("dicom_field", "")
        new_value = mapping.get("new_value", "")

        if not scans_to_correct or not dicom_field or not new_value:
            _logger.warning(f"Invalid mapping: {mapping}")
            continue

        for scan in scans_to_correct:
            if os.path.isdir(os.path.join(export_session_dir, scan)):
                for root, _, files in os.walk(os.path.join(export_session_dir, scan)):
                    for filename in files:
                        if filename.lower().endswith(".dcm"):
                            dicom_path = os.path.join(root, filename)
                            process_dicom_file(dicom_path, dicom_field, new_value)
            else:
                _logger.warning(f"WARNING: Unable to find {scan} to correct DICOMs.")
                _logger.warning("Check that your naming is correct.")


def process_dicom_file(dicom_path, dicom_field, new_value):
    # Read the DICOM file
    ds = pydicom.dcmread(dicom_path)

    # Check if the specified field exists
    if hasattr(ds, dicom_field):

        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            setattr(ds, dicom_field, new_value)

            # Check for warnings
            if any("Invalid value" in str(warning.message) for warning in w):
                _logger.warning(f"{[str(warning.message) for warning in w]}")
                _logger.warning("The requested new value is not valid. DICOM not modified")
            else:
                # Print the modified value of the field if no warnings were raised
                _logger.info(f"Modified {dicom_field} in {dicom_path}: {getattr(ds, dicom_field)}")

                # Save the modified DICOM file in place
                ds.save_as(dicom_path)
                _logger.info(f"Modified DICOM file saved as {dicom_path}")

    else:
        _logger.warning(f"{dicom_field} field is not present in {dicom_path}.")
        return


def convert_mrs(
    subject,
    session_suffix,
    bids_experiment_dir,
    mrs_data_path,
):
    _logger.info("INFO: Converting MR spectroscopy data")

    # create mrs directory within bids/sourcedata to copy DICOMS into
    mrs_sourcedata_dir = os.path.join(
        bids_experiment_dir, "sourcedata", f"sub-{subject}", f"ses-{session_suffix}", "mrs"
    )

    if not os.path.exists(mrs_sourcedata_dir):
        os.makedirs(mrs_sourcedata_dir, exist_ok=True)

    # create mrs directory within bids session directory
    session_dir = os.path.join(bids_experiment_dir, f"sub-{subject}", f"ses-{session_suffix}")

    mrs_bids_dir = os.path.join(session_dir, "mrs")

    if not os.path.exists(mrs_bids_dir):
        os.makedirs(mrs_bids_dir, exist_ok=True)

    # copy MRS DICOM to sourcedata, renaming for BIDS format
    mrs_scan_name = os.path.basename(mrs_data_path)
    mrs_dicomfiles = glob.glob(os.path.join(mrs_data_path, "*.dcm"))

    if len(mrs_dicomfiles) > 1:
        _logger.warning(
            f"WARNING: More than one spectroscopy DICOM per scan. \
                Processing only {mrs_dicomfiles[0]}"
        )

    mrs_keys = str.split(mrs_scan_name, "_")

    bids_mrs_scan_name = (
        f"sub-{subject}_ses-{session_suffix}_"
        f"{'_'.join(mrs_keys[1:])}_"
        f"{str.split(mrs_keys[0],'-')[-1]}"
    )

    mrs_bids_dicomfile = f"{mrs_sourcedata_dir}/{bids_mrs_scan_name}.dcm"
    shutil.copy(mrs_dicomfiles[0], mrs_bids_dicomfile)

    # convert MRS DICOM to NIFTI-MRS and place in bids mrs directory
    spec2nii_command = (
        f"spec2nii dicom -j -f {bids_mrs_scan_name} -o {mrs_bids_dir} {mrs_bids_dicomfile}"
    )
    result = subprocess.run(spec2nii_command, shell=True, capture_output=True, text=True)
    if result.returncode:
        _logger.warning(f"spec2nii failed to convert MRS DICOM {mrs_bids_dicomfile}")
    _logger.debug(result)

    # if the conversion succeeded, add a line to scans.tsv file
    mrs_bids_nii = os.path.join(mrs_bids_dir, f"{bids_mrs_scan_name}.nii.gz")

    if os.path.exists(mrs_bids_nii):
        scans_tsv_filename = f"sub-{subject}_ses-{session_suffix}_scans.tsv"

        # use heudiconv functions to extract info for _scans.tsv file and add to file
        new_row = {
            f"mrs/{bids_mrs_scan_name}.nii.gz": get_formatted_scans_key_row(mrs_bids_dicomfile)
        }
        add_rows_to_scans_keys_file(os.path.join(session_dir, scans_tsv_filename), new_row)
