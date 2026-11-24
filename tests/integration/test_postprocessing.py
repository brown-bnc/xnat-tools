import json
import operator
import os
import shlex
import typing

from typer.testing import CliRunner

from tests.helpers import reset_directory
from xnat_tools.bids_postprocess import bids_postprocess
from xnat_tools.xnat2bids import app as xnat2bids_app

runner = CliRunner()


# TODO #185: This appears to be doing multiple passes at the export?
# TODO #185: They should live as their own tests
def test_postprocessing(
    xnat_user, xnat_password, xnat_bids_root, xnat_host, test_session, test_session2
):
    """Integration test for bids-postprocessing executable"""

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    # NOTE: The study is the same between the same two sessions so we only need to pull it out once
    study1, subject1, session1, session_suffix1 = test_session
    _, subject2, session2, session_suffix2 = test_session2
    skiplist = ["6"]

    # Run xnat2bids against session 1
    xnat2bids_cmd = shlex.split(
        f"{session1} {xnat_bids_root} -u {xnat_user} -p {xnat_password} -s {' -s '.join(skiplist)}"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(xnat2bids_app, xnat2bids_cmd)
    print(r.stdout)

    # Run xnat2bids against session 2
    xnat2bids_split_cmd = shlex.split(
        f"{session2} {xnat_bids_root} -u {xnat_user} -p {xnat_password} --s {' -s '.join(skiplist)}"
    )
    print("Running xnat2bids application:")
    r = runner.invoke(xnat2bids_app, xnat2bids_split_cmd)
    print(r.stdout)

    # TODO: Should this be split between the two sessions?
    # TODO: This is not the correct subdir? Need to strip the BNC folder
    bids_dir = f"{xnat_bids_root}/bnc/study-{study1}/bids"

    # TODO: We should split the "bold" and normal fmaps into separate arrays
    # TODO: This is what we do for the intendedfor below
    subj_005_session1_fmaps = [
        f"{bids_dir}/sub-{subject1}/ses-{session_suffix1}/fmap/sub-{subject1}_ses-{session_suffix1}_acq-boldGRE_phasediff.json",
        f"{bids_dir}/sub-{subject1}/ses-{session_suffix1}/fmap/sub-{subject1}_ses-{session_suffix1}_acq-boldGRE_magnitude1.json",
        f"{bids_dir}/sub-{subject1}/ses-{session_suffix1}/fmap/sub-{subject1}_ses-{session_suffix1}_acq-boldGRE_magnitude2.json",
        f"{bids_dir}/sub-{subject1}/ses-{session_suffix1}/fmap/sub-{subject1}_ses-{session_suffix1}_acq-diffSE_dir-ap_epi.json",
        f"{bids_dir}/sub-{subject1}/ses-{session_suffix1}/fmap/sub-{subject1}_ses-{session_suffix1}_acq-diffSE_dir-pa_epi.json",
    ]

    # TODO: We should split the "bold" and normal fmaps into separate arrays
    subj_005_session2_fmaps = [
        f"{bids_dir}/sub-{subject2}/ses-{session_suffix2}/fmap/sub-{subject2}_ses-{session_suffix2}_acq-boldGRE_phasediff.json",
        f"{bids_dir}/sub-{subject2}/ses-{session_suffix2}/fmap/sub-{subject2}_ses-{session_suffix2}_acq-boldGRE_magnitude1.json",
        f"{bids_dir}/sub-{subject2}/ses-{session_suffix2}/fmap/sub-{subject2}_ses-{session_suffix2}_acq-boldGRE_magnitude2.json",
        f"{bids_dir}/sub-{subject2}/ses-{session_suffix2}/fmap/sub-{subject2}_ses-{session_suffix2}_acq-diffSE_dir-ap_epi.json",
        f"{bids_dir}/sub-{subject2}/ses-{session_suffix2}/fmap/sub-{subject2}_ses-{session_suffix2}_acq-diffSE_dir-pa_epi.json",
    ]

    all_fieldmaps = [*subj_005_session1_fmaps, *subj_005_session2_fmaps]

    session1_bold_intendedfor = [
        f"ses-{session_suffix1}/func/sub-{subject1}_ses-{session_suffix1}_task-checks_run-02_bold.nii.gz",
        f"ses-{session_suffix1}/func/sub-{subject1}_ses-{session_suffix1}_task-resting_bold.nii.gz",
        f"ses-{session_suffix1}/func/sub-{subject1}_ses-{session_suffix1}_task-motionloc_bold.nii.gz",
        f"ses-{session_suffix1}/func/sub-{subject1}_ses-{session_suffix1}_task-checks_run-01_bold.nii.gz",
    ]

    session1_diff_intendedfor = [
        f"ses-{session_suffix1}/dwi/sub-{subject1}_ses-{session_suffix1}_acq-b1500_dir-ap_sbref.nii.gz",
        f"ses-{session_suffix1}/dwi/sub-{subject1}_ses-{session_suffix1}_acq-b1500_dir-ap_dwi.nii.gz",
        f"ses-{session_suffix1}/dwi/sub-{subject1}_ses-{session_suffix1}_acq-b1500_dir-pa_sbref.nii.gz",
        f"ses-{session_suffix1}/dwi/sub-{subject1}_ses-{session_suffix1}_acq-b1500_dir-pa_dwi.nii.gz",
    ]

    # Clean IntendedFor keys from all fieldmaps.
    cleanIntendedForData(all_fieldmaps)

    # Process all sessions with no override.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_password,
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

    # Reset each fieldmaps' IntendedFor property to an test string.
    updateIntendedForData(all_fieldmaps, "test string")

    # Run post-processing with no override.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_password,
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
        xnat_password,
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

    # Delete each fieldmaps' IntendedFor property.
    cleanIntendedForData(all_fieldmaps)

    # Run post-processing, skipping the subject.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_password,
        session="",
        includesess=[],
        includesubj=[],
        # TODO: Should I pass both subject1 and subject2? Even though they're the same?
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
        xnat_password,
        host=xnat_host,
        session="",
        includesess=[session_suffix1],
        # TODO: Should I pass both subject1 and subject2? Even though they're the same?
        includesubj=[subject1],
        skipsubj=[],
        skipsess=[],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    # Verify session1 bold fmaps have not been processed.
    verifyProcessed(subj_005_session1_fmaps[:3], session1_bold_intendedfor)

    # Verify session1 diffusion fmaps have ot been processed.
    verifyProcessed(subj_005_session1_fmaps[3:], session1_diff_intendedfor)

    # Verify session2 fmap has not been processed.
    verifySkipped(subj_005_session2_fmaps)

    # Delete each fieldmaps' IntendedFor property.
    cleanIntendedForData(all_fieldmaps)

    # Run post-processing with includesubj and skipsess.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_password,
        host=xnat_host,
        session="",
        includesess=[],
        includesubj=[subject1],
        skipsubj=[],
        skipsess=[session_suffix2],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    # Verify session1 bold fmaps have been processed.
    # TODO: We should split these arrays in the variables themselves
    verifyProcessed(subj_005_session1_fmaps[:3], session1_bold_intendedfor)

    # Verify session1 diffusion fmaps have been processed.
    # TODO: We should split these arrays in the variables themselves
    verifyProcessed(subj_005_session1_fmaps[3:], session1_diff_intendedfor)

    # Verify session2 fmap has not been processed.
    verifySkipped(subj_005_session2_fmaps)

    # Delete each fieldmaps' IntendedFor property.
    cleanIntendedForData(all_fieldmaps)

    # Run bids_postprocess for a single session.
    bids_postprocess(
        bids_dir,
        xnat_user,
        xnat_password,
        host=xnat_host,
        session=session1,
        includesess=[],
        includesubj=[],
        skipsubj=[],
        skipsess=[],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    # Verify session1 bold fmaps have been processed.
    # TODO: We should split these arrays in the variables themselves
    verifyProcessed(subj_005_session1_fmaps[:3], session1_bold_intendedfor)

    # Verify session1 diffusion fmaps have been processed.
    # TODO: We should split these arrays in the variables themselves
    verifyProcessed(subj_005_session1_fmaps[3:], session1_diff_intendedfor)

    # Verify session2 fmaps have not been processed.
    verifySkipped(subj_005_session2_fmaps)

    # NOTE: you can locally run bids-validator
    # bids_directory=f"{PWD}/{xnat_bids_root}/study-demodat/bids/
    # docker run -ti --rm -v ${bids_directory}:/data:ro bids/validator /data


# -------------------- HELPERS --------------------


def cleanIntendedForData(fieldmaps: list):
    # Delete each fieldmaps' IntendedFor property.
    for json_file in fieldmaps:
        if os.path.isfile(json_file):
            os.chmod(json_file, 0o664)
            with open(json_file, "r") as f:
                data = json.load(f)
                if "IntendedFor" in data:
                    del data["IntendedFor"]
                f.close()
            with open(json_file, "w") as f:
                json.dump(data, f, indent=4, sort_keys=True)
                f.close()


def updateIntendedForData(fieldmaps: list, testData: typing.Any):
    for json_file in fieldmaps:
        os.chmod(json_file, 0o664)
        with open(json_file, "r") as f:
            data = json.load(f)
            data["IntendedFor"] = testData
            f.close()
        with open(json_file, "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)
            f.close()


def verifySkipped(fieldmaps: list):
    for json_file in fieldmaps:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert "IntendedFor" not in data
            f.close()


def verifyProcessed(fieldmaps: list, testSet: list):
    for json_file in fieldmaps:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert sorted(data["IntendedFor"]) == sorted(testSet)
            f.close()


def check_json_data(fieldmaps: list, op: str, value: str):
    rel_ops = {"==": operator.eq, "!=": operator.ne}

    for json_file in fieldmaps:
        with open(json_file, "r") as f:
            data = json.load(f)
            assert rel_ops[op](data["IntendedFor"], value)
            f.close()
