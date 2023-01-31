import glob
import json
import os
import shlex
import shutil

import pydicom
from dotenv import load_dotenv
from typer.testing import CliRunner

from xnat_tools.xnat2bids import app

runner = CliRunner()
load_dotenv()


def series_idx(f):
    """Return series index from filename"""
    ext = f.split(".")[-1]
    if ext == "dcm":
        return f.split("-")[1]
    elif ext == "IMA":
        return f.split(".")[3]
    else:
        return 0


def test_xnat2bids():
    """Integration test for xnat2bids executable"""

    xnat_user = os.environ.get("XNAT_USER", "")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    session = os.environ.get("XNAT_SESSION", "XNAT_E00114")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "session1")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")
    skiplist = ["6"]

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)

    os.mkdir(bids_root_dir)

    xnat2bids_cmd = f"{session} {bids_root_dir} -u {xnat_user} -p {xnat_pass} \
        -s {' -s '.join(skiplist)}"

    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)
    print(xnat2bids_split_cmd)
    r = runner.invoke(app, xnat2bids_split_cmd)
    print(r.stdout)

    assert r.exit_code == 0

    filepath = f"tests/xnat2bids/*/study-*/bids/sub-*/ses-{session_suffix}"

    # ***************************************************************************
    # Test for successful execution
    # ***************************************************************************
    assert len(glob.glob(f"{filepath}/*/*.json")) > 0
    assert len(glob.glob(f"{filepath}/*/*.nii.gz")) > 0

    # ***************************************************************************
    # Test for correctess of sequence number given by skiplist
    # ***************************************************************************
    xnat_export_path = glob.glob(
        f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]
    assert os.path.isdir(os.path.join(os.getcwd(), xnat_export_path))

    export_subdirs = [f.path for f in os.scandir(xnat_export_path) if f.is_dir()]

    for d in export_subdirs:
        series_desc = os.path.basename(d)
        for f in os.listdir(d):
            dataset = pydicom.dcmread(os.path.join(d, f))
            idx = series_idx(f)
            assert str(idx) not in skiplist
            if series_desc.__contains__("SBRef"):
                assert dataset.data_element("ProtocolName").value == series_desc.replace(
                    "_SBRef", ""
                )
                assert dataset.data_element("SeriesDescription").value == series_desc
            else:
                assert dataset.data_element("ProtocolName").value == series_desc
                assert dataset.data_element("SeriesDescription").value == series_desc

    bids_dir = glob.glob("tests/xnat2bids/*/study-*/bids")[0]

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
            f.close

    # Verify session1 diffusion fmaps have been processed.
    for json_file in subj_005_session1_fmaps[3:]:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert sorted(data["IntendedFor"]) == sorted(session1_diff_intendedfor)
            f.close
