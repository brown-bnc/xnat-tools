import glob
import json
import os
import shlex

import pydicom
from typer.testing import CliRunner

from tests.helpers import reset_directory, series_idx
from xnat_tools.xnat2bids import app

runner = CliRunner()


def test_xnat2bids(xnat_user, xnat_password, xnat_bids_root):
    """Integration test for xnat2bids executable"""

    # Define target session
    session = os.environ.get("XNAT_SESSION", "XNAT_E00114")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "session1")

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    skipseq = ["6"]
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
        -s {' -s '.join(skipseq)}"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    filepath = f"{xnat_bids_root}/*/study-*/bids/sub-*/ses-{session_suffix}"

    # ***************************************************************************
    # Test for successful execution
    # ***************************************************************************
    assert len(glob.glob(f"{filepath}/*/*.json")) > 0
    assert len(glob.glob(f"{filepath}/*/*.nii.gz")) > 0

    # ***************************************************************************
    # Test for correctness of sequence number given by skipseq
    # ***************************************************************************
    xnat_export_path = glob.glob(
        f"{xnat_bids_root}/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]
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

    bids_dir = glob.glob("{xnat_bids_root}/*/study-*/bids")[0]

    subj_005_session1_fmaps = [
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-boldGRE_phasediff.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-boldGRE_magnitude1.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-boldGRE_magnitude2.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-diffSE_dir-ap_epi.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-diffSE_dir-pa_epi.json",
    ]
    session1_bold_intendedfor = [
        "ses-session1/func/sub-005_ses-session1_task-checks_run-02_bold.nii.gz",
        "ses-session1/func/sub-005_ses-session1_task-resting_bold.nii.gz",
        "ses-session1/func/sub-005_ses-session1_task-motionloc_bold.nii.gz",
        "ses-session1/func/sub-005_ses-session1_task-checks_run-01_bold.nii.gz",
    ]

    session1_diff_intendedfor = [
        "ses-session1/dwi/sub-005_ses-session1_acq-b1500_dir-ap_sbref.nii.gz",
        "ses-session1/dwi/sub-005_ses-session1_acq-b1500_dir-ap_dwi.nii.gz",
        "ses-session1/dwi/sub-005_ses-session1_acq-b1500_dir-pa_sbref.nii.gz",
        "ses-session1/dwi/sub-005_ses-session1_acq-b1500_dir-pa_dwi.nii.gz",
    ]

    # Verify session1 bold fmaps have been processed.
    for json_file in subj_005_session1_fmaps[:3]:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert sorted(data["IntendedFor"]) == sorted(session1_bold_intendedfor)
            f.close()

    # Verify session1 diffusion fmaps have been processed.
    for json_file in subj_005_session1_fmaps[3:]:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert sorted(data["IntendedFor"]) == sorted(session1_diff_intendedfor)
            f.close()


def test_xnat2bids_export_only(xnat_user, xnat_password, xnat_bids_root):
    # Define target session
    session = os.environ.get("XNAT_SESSION", "XNAT_E00114")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "session1")

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    skipseq = ["6"]
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
        -s {' -s '.join(skipseq)} --export-only"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    xnat_export_path = glob.glob(
        f"{xnat_bids_root}/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]

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


def test_xnat2bids_skip_export(xnat_user, xnat_password, xnat_bids_root):
    # Define target session
    session = os.environ.get("XNAT_SESSION", "XNAT_E00114")

    # TODO #187: This test relies on the previous test (test_xnat2bids_export_only) seeding the xnat_bids_root directory
    # TODO #187: This needs to seed its own dicom export to be independent

    skipseq = ["6"]
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
        -s {' -s '.join(skipseq)} --skip-export"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    bids_dir = glob.glob("{xnat_bids_root}/*/study-*/bids")[0]

    subj_005_session1_fmaps = [
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-boldGRE_phasediff.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-boldGRE_magnitude1.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-boldGRE_magnitude2.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-diffSE_dir-ap_epi.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-diffSE_dir-pa_epi.json",
    ]
    session1_bold_intendedfor = [
        "ses-session1/func/sub-005_ses-session1_task-checks_run-02_bold.nii.gz",
        "ses-session1/func/sub-005_ses-session1_task-resting_bold.nii.gz",
        "ses-session1/func/sub-005_ses-session1_task-motionloc_bold.nii.gz",
        "ses-session1/func/sub-005_ses-session1_task-checks_run-01_bold.nii.gz",
    ]

    session1_diff_intendedfor = [
        "ses-session1/dwi/sub-005_ses-session1_acq-b1500_dir-ap_sbref.nii.gz",
        "ses-session1/dwi/sub-005_ses-session1_acq-b1500_dir-ap_dwi.nii.gz",
        "ses-session1/dwi/sub-005_ses-session1_acq-b1500_dir-pa_sbref.nii.gz",
        "ses-session1/dwi/sub-005_ses-session1_acq-b1500_dir-pa_dwi.nii.gz",
    ]

    # Verify session1 bold fmaps have been processed.
    for json_file in subj_005_session1_fmaps[:3]:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert sorted(data["IntendedFor"]) == sorted(session1_bold_intendedfor)
            f.close()

    # Verify session1 diffusion fmaps have been processed.
    for json_file in subj_005_session1_fmaps[3:]:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert sorted(data["IntendedFor"]) == sorted(session1_diff_intendedfor)
            f.close()


def test_xnat2bids_eeg(xnat_user, xnat_password, xnat_bids_root):
    """Integration test for xnat2bids executable converting EEG data to BIDS"""

    # Define target session
    # NOTE: "BNC Demo Dataset" does not contain EEG data, test against a session that does
    session = os.environ.get("XNAT_SESSION", "XNAT_E00474")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "01")

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    skipseq = ["6"]
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
        -s {' -s '.join(skipseq)}"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    filepath = f"{xnat_bids_root}/*/study-*/bids/sub-*/ses-{session_suffix}"

    # ***************************************************************************
    # Test for successful execution
    # ***************************************************************************
    assert len(glob.glob(f"{filepath}/*/*.json")) > 0
    assert len(glob.glob(f"{filepath}/*/*.nii.gz")) > 0

    # ***************************************************************************
    # Test for successful BIDS conversion of EEG data
    # ***************************************************************************
    bids_dir = glob.glob("{xnat_bids_root}/*/study-*/bids")[0]

    subj_bncmethods_ses_01_eeg = [
        f"{bids_dir}/sub-bncmethods/ses-01/eeg/sub-bncmethods_ses-01_task-todo_eeg.eeg",
        f"{bids_dir}/sub-bncmethods/ses-01/eeg/sub-bncmethods_ses-01_task-todo_eeg.json",
        f"{bids_dir}/sub-bncmethods/ses-01/eeg/sub-bncmethods_ses-01_task-todo_eeg.vhdr",
        f"{bids_dir}/sub-bncmethods/ses-01/eeg/sub-bncmethods_ses-01_task-todo_eeg.vmrk",
        f"{bids_dir}/sub-bncmethods/ses-01/eeg/sub-bncmethods_ses-01_task-todo_events.json",
        f"{bids_dir}/sub-bncmethods/ses-01/eeg/sub-bncmethods_ses-01_task-todo_events.tsv",
    ]

    # Verify session1 diffusion fmaps have been processed.
    for eeg_file in subj_bncmethods_ses_01_eeg:
        assert os.path.isfile(eeg_file)


def test_xnat2bids_correct_dicom_header(xnat_user, xnat_password, xnat_bids_root):
    # Define target session
    session = os.environ.get("XNAT_SESSION", "XNAT_E00114")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "session1")

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    includeseq = "17"
    dicom_fix_config_file = "./tests/dicom_fix_config_invalid_value.json"
    xnat2bids_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} \
        -i {includeseq} --export-only --dicomfix-config {dicom_fix_config_file}"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(app, xnat2bids_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    xnat_export_path = glob.glob(
        f"{xnat_bids_root}/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]

    export_subdirs = [f.path for f in os.scandir(xnat_export_path) if f.is_dir()]

    for d in export_subdirs:
        for f in os.listdir(d):
            dataset = pydicom.dcmread(os.path.join(d, f))
            # first test if we successfully changed the Patient ID to "Anonymous"
            assert dataset.data_element("PatientID").value == "Anonymous"
            # then test that we did not change the Study Date to an invalid date
            assert dataset.data_element("StudyDate").value != "20240435"
