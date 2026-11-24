import json
import operator
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

    # TODO: This test assumes test_session and test_session2 are a part of the same project
    # TODO: But the variables can be overridden so this is not necessarily the case

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    # Define target sessions
    session_data1, session_data_clean1, session_suffix_path_prefixes1 = test_session
    project1, subject1, session1, session_suffix1 = session_data1
    project_clean1, subject_clean1, session_suffix_clean1 = session_data_clean1
    pi_path_prefix1, project_path_prefix1, subject_path_prefix1, session_suffix_path_prefix1 = (
        session_suffix_path_prefixes1
    )
    session_data2, session_data_clean2, session_suffix_path_prefixes2 = test_session2
    # NOTE: The project is the same between the two sessions so we only need to pull it out once
    project2, subject2, session2, session_suffix2 = session_data2
    project_clean2, subject_clean2, session_suffix_clean2 = session_data_clean2
    pi_path_prefix2, project_path_prefix2, subject_path_prefix2, session_suffix_path_prefix2 = (
        session_suffix_path_prefixes2
    )

    # TODO: Is this fixed to the specific study? Does it need to be a part of the fixture?
    skiplist = ["6"]

    # Run xnat2bids against session 1
    xnat2bids_cmd = shlex.split(
        f"{session1} {xnat_bids_root} -u {xnat_user} -p {xnat_password} -s {' -s '.join(skiplist)}"
    )
    print("Running xnat2bids application (session 1):")
    r = runner.invoke(xnat2bids_app, xnat2bids_cmd)
    print(r.stdout)

    # Run xnat2bids against session 2
    xnat2bids_split_cmd = shlex.split(
        f"{session2} {xnat_bids_root} -u {xnat_user} -p {xnat_password} -s {' -s '.join(skiplist)}"
    )
    print("Running xnat2bids application (session 2):")
    r = runner.invoke(xnat2bids_app, xnat2bids_split_cmd)
    print(r.stdout)

    # TODO: This assumes both test sessions are a part of the same project (e.g. same bids_dir)
    bids_dir = xnat_bids_root / pi_path_prefix1 / project_path_prefix1 / "bids"

    fmap_dir1 = bids_dir / subject_path_prefix1 / session_suffix_path_prefix1 / "fmap"
    file_prefix1 = f"{subject_path_prefix1}_{session_suffix_path_prefix1}"
    fmap_dir2 = bids_dir / subject_path_prefix2 / session_suffix_path_prefix2 / "fmap"
    file_prefix2 = f"{subject_path_prefix2}_{session_suffix_path_prefix2}"

    session1_bold_fmaps = [
        fmap_dir1 / f"{file_prefix1}_acq-boldGRE_phasediff.json",
        fmap_dir1 / f"{file_prefix1}_acq-boldGRE_magnitude1.json",
        fmap_dir1 / f"{file_prefix1}_acq-boldGRE_magnitude2.json",
    ]
    session1_diff_fmaps = [
        fmap_dir1 / f"{file_prefix1}_acq-diffSE_dir-ap_epi.json",
        fmap_dir1 / f"{file_prefix1}_acq-diffSE_dir-pa_epi.json",
    ]
    session1_fmaps = [*session1_bold_fmaps, *session1_diff_fmaps]

    session2_bold_fmaps = [
        fmap_dir2 / f"{file_prefix2}_acq-boldGRE_phasediff.json",
        fmap_dir2 / f"{file_prefix2}_acq-boldGRE_magnitude1.json",
        fmap_dir2 / f"{file_prefix2}_acq-boldGRE_magnitude2.json",
    ]
    session2_diff_fmaps = [
        fmap_dir2 / f"{file_prefix2}_acq-diffSE_dir-ap_epi.json",
        fmap_dir2 / f"{file_prefix2}_acq-diffSE_dir-pa_epi.json",
    ]
    session2_fmaps = [*session2_bold_fmaps, *session2_diff_fmaps]

    all_fieldmaps = [*session1_fmaps, *session2_fmaps]

    # NOTE: IntendedFor entries are strings stored in the BIDS JSON, not filesystem paths
    # TODO: Do these need the full path?
    session1_bold_intendedfor = [
        f"{session_suffix_path_prefix1}/func/{file_prefix1}_task-checks_run-02_bold.nii.gz",
        f"{session_suffix_path_prefix1}/func/{file_prefix1}_task-resting_bold.nii.gz",
        f"{session_suffix_path_prefix1}/func/{file_prefix1}_task-motionloc_bold.nii.gz",
        f"{session_suffix_path_prefix1}/func/{file_prefix1}_task-checks_run-01_bold.nii.gz",
    ]

    session1_diff_intendedfor = [
        f"{session_suffix_path_prefix1}/dwi/{file_prefix1}_acq-b1500_dir-ap_sbref.nii.gz",
        f"{session_suffix_path_prefix1}/dwi/{file_prefix1}_acq-b1500_dir-ap_dwi.nii.gz",
        f"{session_suffix_path_prefix1}/dwi/{file_prefix1}_acq-b1500_dir-pa_sbref.nii.gz",
        f"{session_suffix_path_prefix1}/dwi/{file_prefix1}_acq-b1500_dir-pa_dwi.nii.gz",
    ]

    # Clean IntendedFor keys from all fieldmaps.
    cleanIntendedForData(all_fieldmaps)

    # Process all sessions with no override.
    bids_postprocess(
        str(bids_dir),
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
        str(bids_dir),
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
        str(bids_dir),
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
        str(bids_dir),
        xnat_user,
        xnat_password,
        session="",
        includesess=[],
        includesubj=[],
        # TODO: Can I use the raw values here instead?
        # TODO: The two subjects here are the same, make sure the tests still pass
        # skipsubj=[subject_clean1],
        skipsubj=[subject_clean1, subject_clean2],
        skipsess=[],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    verifySkipped(all_fieldmaps)

    # Run post-processing with includesubj and includesess.
    bids_postprocess(
        str(bids_dir),
        xnat_user,
        xnat_password,
        host=xnat_host,
        session="",
        includesess=[session_suffix1],
        # TODO: Can I use the raw values here instead?
        # TODO: The two subjects here are the same, make sure the tests still pass
        # includesubj=[subject_clean1],
        includesubj=[subject_clean1, subject_clean2],
        skipsubj=[],
        skipsess=[],
        log_file="",
        verbose=0,
        overwrite=False,
    )

    # Verify session1 bold fmaps have not been processed.
    verifyProcessed(session1_bold_fmaps, session1_bold_intendedfor)

    # Verify session1 diffusion fmaps have not been processed.
    verifyProcessed(session1_diff_fmaps, session1_diff_intendedfor)

    # Verify session2 fmap has not been processed.
    verifySkipped(session2_fmaps)

    # Delete each fieldmaps' IntendedFor property.
    cleanIntendedForData(all_fieldmaps)

    # Run post-processing with includesubj and skipsess.
    bids_postprocess(
        str(bids_dir),
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
    verifyProcessed(session1_bold_fmaps, session1_bold_intendedfor)

    # Verify session1 diffusion fmaps have been processed.
    verifyProcessed(session1_diff_fmaps, session1_diff_intendedfor)

    # Verify session2 fmap has not been processed.
    verifySkipped(session2_fmaps)

    # Delete each fieldmaps' IntendedFor property.
    cleanIntendedForData(all_fieldmaps)

    # Run bids_postprocess for a single session.
    bids_postprocess(
        str(bids_dir),
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
    verifyProcessed(session1_bold_fmaps, session1_bold_intendedfor)

    # Verify session1 diffusion fmaps have been processed.
    verifyProcessed(session1_diff_fmaps, session1_diff_intendedfor)

    # Verify session2 fmap has not been processed.
    verifySkipped(session2_fmaps)

    # NOTE: you can locally run bids-validator
    # bids_directory=f"{PWD}/{xnat_bids_root}/study-demodat/bids/
    # docker run -ti --rm -v ${bids_directory}:/data:ro bids/validator /data


# -------------------- HELPERS --------------------


def cleanIntendedForData(fieldmaps: list):
    # Delete each fieldmaps' IntendedFor property.
    for json_file in fieldmaps:
        if json_file.is_file():
            json_file.chmod(0o664)
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
        json_file.chmod(0o664)
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
