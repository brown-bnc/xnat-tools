import glob
import json
import operator
import os
import shlex
import shutil
import subprocess
import typing

from dotenv import load_dotenv
from typer.testing import CliRunner

from xnat_tools.bids_postprocess import bids_postprocess
from xnat_tools.xnat2bids import app as xnat2bids_app

runner = CliRunner()
load_dotenv()


def test_postprocessing():
    """Integration test for bids-postprocessing executable"""
    xnat_user = os.environ.get("XNAT_USER", "")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    subj5_session = "XNAT_E00114"
    subj5_session2 = "XNAT_E00152"
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)

    os.mkdir(bids_root_dir)

    xnat2bids_cmd = f"{subj5_session} {bids_root_dir} -u {xnat_user} -p {xnat_pass} -s 6"

    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)

    r = runner.invoke(xnat2bids_app, xnat2bids_split_cmd)
    print(r.stdout)

    xnat2bids_cmd = f"{subj5_session2} {bids_root_dir} -u {xnat_user} -p {xnat_pass} -s 6"

    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)

    r = runner.invoke(xnat2bids_app, xnat2bids_split_cmd)
    print(r.stdout)

    bids_dir = "tests/xnat2bids/bnc/study-demodat/bids"

    subj_005_session1_fmaps = [
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-boldGRE_phasediff.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-boldGRE_magnitude1.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-boldGRE_magnitude2.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-diffSE_dir-ap_epi.json",
        f"{bids_dir}/sub-005/ses-session1/fmap/sub-005_ses-session1_acq-diffSE_dir-pa_epi.json",
    ]

    subj_005_session2_fmaps = [
        f"{bids_dir}/sub-005/ses-session2/fmap/sub-005_ses-session2_acq-boldGRE_phasediff.json",
        f"{bids_dir}/sub-005/ses-session2/fmap/sub-005_ses-session2_acq-boldGRE_magnitude1.json",
        f"{bids_dir}/sub-005/ses-session2/fmap/sub-005_ses-session2_acq-boldGRE_magnitude2.json",
        f"{bids_dir}/sub-005/ses-session2/fmap/sub-005_ses-session2_acq-diffSE_dir-ap_epi.json",
        f"{bids_dir}/sub-005/ses-session2/fmap/sub-005_ses-session2_acq-diffSE_dir-pa_epi.json",
    ]

    all_fieldmaps = [*subj_005_session1_fmaps, *subj_005_session2_fmaps]

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

    # Clean IntendedFor keys from all fieldmaps.
    cleanIntendedForData(all_fieldmaps)

    # Process all sessions with no override.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_pass,
        session="",
        includesess=[],
        includesubj=[],
        skipsubj=[],
        skipsess=[],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    # Verify all IntendedFor fields across all fieldmaps have been populated.
    check_json_data(all_fieldmaps, "!=", "")

    # Run BIDS Validator
    validateBIDS(bids_root_dir)

    # Reset each fieldmap's IntendedFor property to an test string.
    updateIntendedForData(all_fieldmaps, "test string")

    # Run post-processing with no override.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_pass,
        session="",
        includesess=[],
        includesubj=[],
        skipsubj=[],
        skipsess=[],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    # Verify test string data has not been overwritten.
    check_json_data(all_fieldmaps, "==", "test string")

    # Run post-processing with --overwrite.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_pass,
        session="",
        includesess=[],
        includesubj=[],
        skipsubj=[],
        skipsess=[],
        log_file="",
        verbose=0,
        overwrite=True,
    )

    # Verify all IntendedFor fields across all fieldmaps have been overwritten.
    check_json_data(all_fieldmaps, "!=", "test string")

    # Delete each fieldmap's IntendedFor property.
    cleanIntendedForData(all_fieldmaps)

    # Run post-processing, skipping subject 005.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_pass,
        session="",
        includesess=[],
        includesubj=[],
        skipsubj=["005"],
        skipsess=[],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    verifySkipped(all_fieldmaps)

    # Run post-processing with includesubj and includesess.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_pass,
        session="",
        includesess=["session1"],
        includesubj=["005"],
        skipsubj=[],
        skipsess=[],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    # Verify session1 bold fmaps have ot been processed.
    verifyProcessed(subj_005_session1_fmaps[:3], session1_bold_intendedfor)

    # Verify session1 diffusion fmaps have ot been processed.
    verifyProcessed(subj_005_session1_fmaps[3:], session1_diff_intendedfor)

    # Verify session2 fmap has not been processed.
    verifySkipped(subj_005_session2_fmaps)

    # Delete each fieldmap's IntendedFor property.
    cleanIntendedForData(all_fieldmaps)

    # Run post-processing with includesubj and skipsess.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_pass,
        session="",
        includesess=[],
        includesubj=["005"],
        skipsubj=[],
        skipsess=["session2"],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    # Verify session1 bold fmaps have been processed.
    verifyProcessed(subj_005_session1_fmaps[:3], session1_bold_intendedfor)

    # Verify session1 diffusion fmaps have been processed.
    verifyProcessed(subj_005_session1_fmaps[3:], session1_diff_intendedfor)

    # Verify session2 fmap has not been processed.
    verifySkipped(subj_005_session2_fmaps)

    # Delete each fieldmap's IntendedFor property.
    cleanIntendedForData(all_fieldmaps)

    # Run bids_postprocess for a single session.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_pass,
        session="XNAT_E00114",
        includesess=[],
        includesubj=[],
        skipsubj=[],
        skipsess=[],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    # Verify session1 bold fmaps have been processed.
    verifyProcessed(subj_005_session1_fmaps[:3], session1_bold_intendedfor)

    # Verify session1 diffusion fmaps have been processed.
    verifyProcessed(subj_005_session1_fmaps[3:], session1_diff_intendedfor)

    # Verify session2 fmaps have not been processed.
    verifySkipped(subj_005_session2_fmaps)

    # cleanup output -- for debugging commsent this out
    shutil.rmtree(bids_root_dir, ignore_errors=True)

    # you can locally run bids-validator
    # bids_directory=${PWD}/tests/xnat2bids/study-demodat/bids/
    # docker run -ti --rm -v ${bids_directory}:/data:ro bids/validator /data


def cleanIntendedForData(fieldmaps: list):
    # Delete each fieldmap's IntendedFor property.
    for json_file in fieldmaps:
        if os.path.isfile(json_file):
            os.chmod(json_file, 0o664)
            with open(json_file, "r") as f:
                data = json.load(f)
                if "IntendedFor" in data:
                    del data["IntendedFor"]
                f.close
            with open(json_file, "w") as f:
                json.dump(data, f, indent=4, sort_keys=True)
                f.close


def updateIntendedForData(fieldmaps: list, testData: typing.Any):
    for json_file in fieldmaps:
        os.chmod(json_file, 0o664)
        with open(json_file, "r") as f:
            data = json.load(f)
            data["IntendedFor"] = testData
            f.close
        with open(json_file, "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)
            f.close


def verifySkipped(fieldmaps: list):
    for json_file in fieldmaps:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert "IntendedFor" not in data
            f.close


def verifyProcessed(fieldmaps: list, testSet: list):
    for json_file in fieldmaps:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert sorted(data["IntendedFor"]) == sorted(testSet)
            f.close


def check_json_data(fieldmaps: list, op: str, value: str):
    rel_ops = {"==": operator.eq, "!=": operator.ne}

    for json_file in fieldmaps:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert rel_ops[op](data["IntendedFor"], value)
            f.close


def validateBIDS(bids_root_dir: str):
    bids_path = glob.glob(f"{bids_root_dir}/*/study-*/bids/")[0]
    f = open("issues.txt", "w")
    subprocess.run(shlex.split(f"bids-validator {bids_path}"), stdout=f)

    with open("issues.txt", "r") as bids_issues:
        for line in bids_issues:
            assert "ERR" not in line
