import glob
import json
import os
import shlex

import pydicom
from typer.testing import CliRunner

from tests.helpers import reset_directory, series_idx
from xnat_tools.xnat2bids import app

runner = CliRunner()

# TODO: The breakdown of these tests is a little weird
# TODO: The second test is just the first half of the first test
# TODO: And the third test is just the second half of the first test


def test_xnat2bids(xnat_user, xnat_password, xnat_bids_root, test_session):
    """Integration test for xnat2bids executable"""

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    # Define target session
    session_data, session_data_clean, session_path_prefixes = test_session
    project, subject, session, session_suffix = session_data
    project_clean, subject_clean, session_clean, session_suffix_clean = session_data_clean
    pi_path_prefix, project_path_prefix, subject_path_prefix, session_path_prefix = (
        session_path_prefixes
    )
    # TODO: skipseq is dependent on the specific session we use. Pull into the fixture?
    skipseq = ["6"]

    # Run xnat2bids
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
        -s {' -s '.join(skipseq)}"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    # ***************************************************************************
    # Test for successful execution
    # ***************************************************************************

    bids_path = f"{xnat_bids_root}/{pi_path_prefix}/{project_path_prefix}/bids/{subject_path_prefix}/{session_path_prefix}"

    assert len(glob.glob(f"{bids_path}/*/*.json")) > 0
    assert len(glob.glob(f"{bids_path}/*/*.nii.gz")) > 0

    # ***************************************************************************
    # Test for correctness of sequence number given by skipseq
    # ***************************************************************************

    xnat_export_path = f"{xnat_bids_root}/{pi_path_prefix}/{project_path_prefix}/xnat_export/{subject_path_prefix}/{session_path_prefix}"

    assert os.path.isdir(os.path.join(os.getcwd(), xnat_export_path))

    export_subdirs = [f.path for f in os.scandir(xnat_export_path) if f.is_dir()]
    for d in export_subdirs:
        series_desc = os.path.basename(d)
        for f in os.listdir(d):
            dataset = pydicom.dcmread(os.path.join(d, f))
            idx = series_idx(f)
            assert str(idx) not in skipseq
            if series_desc.__contains__("SBRef"):
                assert dataset.data_element("ProtocolName").value == series_desc.replace(
                    "_SBRef", ""
                )
                assert dataset.data_element("SeriesDescription").value == series_desc
            else:
                assert dataset.data_element("ProtocolName").value == series_desc
                assert dataset.data_element("SeriesDescription").value == series_desc

    # The base .../bids directory
    bids_dir = f"{xnat_bids_root}/{pi_path_prefix}/{project_path_prefix}/bids"

    session_bold_fmaps = [
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/fmap/{subject_path_prefix}_{session_path_prefix}_acq-boldGRE_phasediff.json",
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/fmap/{subject_path_prefix}_{session_path_prefix}_acq-boldGRE_magnitude1.json",
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/fmap/{subject_path_prefix}_{session_path_prefix}_acq-boldGRE_magnitude2.json",
    ]
    session_diff_fmaps = [
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/fmap/{subject_path_prefix}_{session_path_prefix}_acq-diffSE_dir-ap_epi.json",
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/fmap/{subject_path_prefix}_{session_path_prefix}_acq-diffSE_dir-pa_epi.json",
    ]
    session_bold_intendedfor = [
        f"{session_path_prefix}/func/{subject_path_prefix}_{session_path_prefix}_task-checks_run-02_bold.nii.gz",
        f"{session_path_prefix}/func/{subject_path_prefix}_{session_path_prefix}_task-resting_bold.nii.gz",
        f"{session_path_prefix}/func/{subject_path_prefix}_{session_path_prefix}_task-motionloc_bold.nii.gz",
        f"{session_path_prefix}/func/{subject_path_prefix}_{session_path_prefix}_task-checks_run-01_bold.nii.gz",
    ]
    session_diff_intendedfor = [
        f"{session_path_prefix}/dwi/{subject_path_prefix}_{session_path_prefix}_acq-b1500_dir-ap_sbref.nii.gz",
        f"{session_path_prefix}/dwi/{subject_path_prefix}_{session_path_prefix}_acq-b1500_dir-ap_dwi.nii.gz",
        f"{session_path_prefix}/dwi/{subject_path_prefix}_{session_path_prefix}_acq-b1500_dir-pa_sbref.nii.gz",
        f"{session_path_prefix}/dwi/{subject_path_prefix}_{session_path_prefix}_acq-b1500_dir-pa_dwi.nii.gz",
    ]

    # Verify session1 bold fmaps have been processed.
    for json_file in session_bold_fmaps:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert sorted(data["IntendedFor"]) == sorted(session_bold_intendedfor)
            f.close()

    # Verify session1 diffusion fmaps have been processed.
    for json_file in session_diff_fmaps:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert sorted(data["IntendedFor"]) == sorted(session_diff_intendedfor)
            f.close()


def test_xnat2bids_export_only(xnat_user, xnat_password, xnat_bids_root, test_session):
    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    # Define target session
    session_data, session_data_clean, session_path_prefixes = test_session
    project, subject, session, session_suffix = session_data
    project_clean, subject_clean, session_clean, session_suffix_clean = session_data_clean
    pi_path_prefix, project_path_prefix, subject_path_prefix, session_path_prefix = (
        session_path_prefixes
    )
    # TODO: skipseq is dependent on the specific session we use. Pull into the fixture?
    skipseq = ["6"]

    # Run xnat2bids
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
        -s {' -s '.join(skipseq)} --export-only"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    xnat_export_path = f"{xnat_bids_root}/{pi_path_prefix}/{project_path_prefix}/xnat_export/{subject_path_prefix}/{session_path_prefix}"

    assert os.path.isdir(os.path.join(os.getcwd(), xnat_export_path))

    export_subdirs = [f.path for f in os.scandir(xnat_export_path) if f.is_dir()]
    for d in export_subdirs:
        series_desc = os.path.basename(d)
        for f in os.listdir(d):
            dataset = pydicom.dcmread(os.path.join(d, f))
            idx = series_idx(f)
            assert str(idx) not in skipseq
            if series_desc.__contains__("SBRef"):
                assert dataset.data_element("ProtocolName").value == series_desc.replace(
                    "_SBRef", ""
                )
                assert dataset.data_element("SeriesDescription").value == series_desc
            else:
                assert dataset.data_element("ProtocolName").value == series_desc
                assert dataset.data_element("SeriesDescription").value == series_desc


def test_xnat2bids_skip_export(xnat_user, xnat_password, xnat_bids_root, test_session):

    # TODO #187: This test relies on the previous test (test_xnat2bids_export_only) seeding the
    # TODO #187 xnat_bids_root directory. This needs to seed its own dicom export to be independent

    # Define target session
    session_data, session_data_clean, session_path_prefixes = test_session
    project, subject, session, session_suffix = session_data
    project_clean, subject_clean, session_clean, session_suffix_clean = session_data_clean
    pi_path_prefix, project_path_prefix, subject_path_prefix, session_path_prefix = (
        session_path_prefixes
    )
    # TODO: skipseq is dependent on the specific session we use. Pull into the fixture?
    skipseq = ["6"]

    # Run xnat2bids
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
        -s {' -s '.join(skipseq)} --skip-export"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    # The base .../bids directory
    bids_dir = f"{xnat_bids_root}/{pi_path_prefix}/{project_path_prefix}/bids"

    session_bold_fmaps = [
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/fmap/{subject_path_prefix}_{session_path_prefix}_acq-boldGRE_phasediff.json",
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/fmap/{subject_path_prefix}_{session_path_prefix}_acq-boldGRE_magnitude1.json",
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/fmap/{subject_path_prefix}_{session_path_prefix}_acq-boldGRE_magnitude2.json",
    ]
    session_diff_fmaps = [
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/fmap/{subject_path_prefix}_{session_path_prefix}_acq-diffSE_dir-ap_epi.json",
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/fmap/{subject_path_prefix}_{session_path_prefix}_acq-diffSE_dir-pa_epi.json",
    ]
    session_bold_intendedfor = [
        f"{session_path_prefix}/func/{subject_path_prefix}_{session_path_prefix}_task-checks_run-02_bold.nii.gz",
        f"{session_path_prefix}/func/{subject_path_prefix}_{session_path_prefix}_task-resting_bold.nii.gz",
        f"{session_path_prefix}/func/{subject_path_prefix}_{session_path_prefix}_task-motionloc_bold.nii.gz",
        f"{session_path_prefix}/func/{subject_path_prefix}_{session_path_prefix}_task-checks_run-01_bold.nii.gz",
    ]
    session_diff_intendedfor = [
        f"{session_path_prefix}/dwi/{subject_path_prefix}_{session_path_prefix}_acq-b1500_dir-ap_sbref.nii.gz",
        f"{session_path_prefix}/dwi/{subject_path_prefix}_{session_path_prefix}_acq-b1500_dir-ap_dwi.nii.gz",
        f"{session_path_prefix}/dwi/{subject_path_prefix}_{session_path_prefix}_acq-b1500_dir-pa_sbref.nii.gz",
        f"{session_path_prefix}/dwi/{subject_path_prefix}_{session_path_prefix}_acq-b1500_dir-pa_dwi.nii.gz",
    ]

    # Verify session1 bold fmaps have been processed.
    for json_file in session_bold_fmaps:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert sorted(data["IntendedFor"]) == sorted(session_bold_intendedfor)
            f.close()

    # Verify session1 diffusion fmaps have been processed.
    for json_file in session_diff_fmaps:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert sorted(data["IntendedFor"]) == sorted(session_diff_intendedfor)
            f.close()


def test_xnat2bids_eeg(xnat_user, xnat_password, xnat_bids_root, eeg_session):
    """Integration test for xnat2bids executable converting EEG data to BIDS"""

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    # Define target session
    session_data, session_data_clean, session_path_prefixes = eeg_session
    project, subject, session, session_suffix = session_data
    project_clean, subject_clean, session_clean, session_suffix_clean = session_data_clean
    pi_path_prefix, project_path_prefix, subject_path_prefix, session_path_prefix = (
        session_path_prefixes
    )
    # TODO: skipseq is dependent on the specific session we use. Pull into the fixture?
    skipseq = ["6"]

    # Run xnat2bids
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
        -s {' -s '.join(skipseq)}"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    # ***************************************************************************
    # Test for successful execution
    # ***************************************************************************

    bids_path = f"{xnat_bids_root}/{pi_path_prefix}/{project_path_prefix}/bids/{subject_path_prefix}/{session_path_prefix}"

    assert len(glob.glob(f"{bids_path}/*/*.json")) > 0
    assert len(glob.glob(f"{bids_path}/*/*.nii.gz")) > 0

    # ***************************************************************************
    # Test for successful BIDS conversion of EEG data
    # ***************************************************************************

    # The base .../bids directory
    bids_dir = f"{xnat_bids_root}/{pi_path_prefix}/{project_path_prefix}/bids"

    # TODO: All of these need to be computed from the fixtures
    session_eeg = [
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/eeg/{subject_path_prefix}_{session_path_prefix}_task-todo_eeg.eeg",
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/eeg/{subject_path_prefix}_{session_path_prefix}_task-todo_eeg.json",
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/eeg/{subject_path_prefix}_{session_path_prefix}_task-todo_eeg.vhdr",
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/eeg/{subject_path_prefix}_{session_path_prefix}_task-todo_eeg.vmrk",
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/eeg/{subject_path_prefix}_{session_path_prefix}_task-todo_events.json",
        f"{bids_dir}/{subject_path_prefix}/{session_path_prefix}/eeg/{subject_path_prefix}_{session_path_prefix}_task-todo_events.tsv",
    ]

    # Verify session1 diffusion fmaps have been processed.
    for eeg_file in session_eeg:
        assert os.path.isfile(eeg_file)


def test_xnat2bids_correct_dicom_header(xnat_user, xnat_password, xnat_bids_root, test_session):
    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    # Define target session
    session_data, session_data_clean, session_path_prefixes = test_session
    project, subject, session, session_suffix = session_data
    project_clean, subject_clean, session_clean, session_suffix_clean = session_data_clean
    pi_path_prefix, project_path_prefix, subject_path_prefix, session_path_prefix = (
        session_path_prefixes
    )
    # TODO: includeseq is dependent on the specific session we use. Pull into the fixture?
    includeseq = ["17"]
    dicom_fix_config_file = "./tests/dicom_fix_config_invalid_value.json"

    # Run xnat2bids
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
        -i {' -i '.join(includeseq)} --export-only --dicomfix-config {dicom_fix_config_file}"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    xnat_export_path = f"{xnat_bids_root}/{pi_path_prefix}/{project_path_prefix}/xnat_export/{subject_path_prefix}/{session_path_prefix}"
    export_subdirs = [f.path for f in os.scandir(xnat_export_path) if f.is_dir()]
    for d in export_subdirs:
        for f in os.listdir(d):
            dataset = pydicom.dcmread(os.path.join(d, f))
            # first test if we successfully changed the Patient ID to "Anonymous"
            assert dataset.data_element("PatientID").value == "Anonymous"
            # then test that we did not change the Study Date to an invalid date
            assert dataset.data_element("StudyDate").value != "20240435"
