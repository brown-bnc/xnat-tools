import glob
import os
import shlex

from typer.testing import CliRunner

from tests.helpers import reset_directory, series_idx
from xnat_tools.dicom_export import app as export_app
from xnat_tools.dicom_export import dicom_export
from xnat_tools.run_heudiconv import app as heudi_app

runner = CliRunner()


def test_dicom_export(xnat_user, xnat_password, xnat_bids_root, xnat_host):
    """Integration test for xnat-dicom-export"""

    # Define target session
    project = os.environ.get("XNAT_PROJECT", "bnc_demodat")
    subject = os.environ.get("XNAT_SUBJECT", "005")
    session = os.environ.get("XNAT_SESSION", "XNAT_E00114")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "-1")

    # Reset the xnat_bids_root directory
    reset_directory(xnat_bids_root)

    # ***************************************************************************
    # Test for successful execution
    # Here we call the function directly. Note, that at the moment, when calling
    # the function, the default values are not correct.
    # See https://github.com/tiangolo/typer/issues/106
    # ***************************************************************************

    p, s, ss = dicom_export(
        session,
        xnat_bids_root,
        user=xnat_user,
        password=xnat_password,
        host=xnat_host,
        session_suffix=session_suffix,
        bidsmap_file="",
        includeseq=["10"],
        skipseq=[],
        log_id="pytest",
        verbose=0,
        overwrite=False,
        validate_frames=False,
        correct_dicoms_config="",
    )

    assert p == project
    assert s == subject
    assert ss == "session1"

    filepath = glob.glob(f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{ss}")[0]

    assert (
        len(glob.glob(f"{filepath}/*/*.IMA")) > 0
        or len(glob.glob(f"{filepath}/*/*.dcm")) > 0
    )
    subdirs = [f.path for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 1
    for d in subdirs:
        for f in os.listdir(d):
            idx = series_idx(f)
            assert idx == "10"

    # ***************************************************************************
    # Test that default overwrite flag is NOT wiping the xnat-export directory
    # Here we test using typer's CLIRunner
    # ***************************************************************************

    export_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} -i 8 -v"
    )
    print("Running dicom_export application:")
    r = runner.invoke(export_app, export_cmd)
    print(r.stdout)

    filepath = glob.glob(f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{ss}")[0]
    subdirs = [f.path for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 2

    for d in subdirs:
        for f in os.listdir(d):
            idx = series_idx(f)
            assert idx in ["8", "10"]

    # # ***************************************************************************
    # # Test that overwrite flag is wiping the xnat-export directory
    # # ***************************************************************************

    export_cmd = shlex.split(
        f"{session} {xnat_bids_root} -u {xnat_user} -p {xnat_password} -v -i 10 --overwrite"
    )
    print("Running dicom_export application:")
    r = runner.invoke(export_app, export_cmd)
    print(r.stdout)

    filepath = glob.glob(f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{ss}")[0]
    subdirs = [f.path for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 1

    for d in subdirs:
        for f in os.listdir(d):
            idx = series_idx(f)
            assert idx == "10"


def test_heudiconv(xnat_bids_root):
    """Integration test for running the run-heudiconv executable on the output
    of xnat-dicom-export"""

    # Define target session
    project = os.environ.get("XNAT_PROJECT", "bnc_demodat")
    subject = os.environ.get("XNAT_SUBJECT", "005")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "session1")

    # TODO #186: This test relies on the previous test (test_dicom_export) seeding the xnat_bids_root directory
    # TODO #186: This needs to seed its own dicom export to be independent

    # ***************************************************************************
    # Test for successful execution
    # ***************************************************************************

    run_heudiconv_cmd = shlex.split(
        f"{project} {subject} {xnat_bids_root} --session-suffix {session_suffix}"
    )
    print("Running run_heudiconv application:")
    r = runner.invoke(heudi_app, run_heudiconv_cmd)
    print(r.stdout)

    try:
        filepath = glob.glob(
            f"tests/xnat2bids/*/study-*/bids/sub-*/ses-{session_suffix}"
        )[0]
    except Exception:
        cmd = "ls tests/xnat2bids/bnc/study-demodat/bids/sub-005/ses-session1"
        os.system(cmd)
        print(
            "Index error at: ",
            glob.glob(f"tests/xnat2bids/*/study-*/bids/sub-*/ses-{session_suffix}"),
        )

    assert r.exit_code == 0

    assert (
        len(glob.glob(f"{filepath}/*/*.json")) > 0
        or len(glob.glob(f"{filepath}/*/*.nii.gz")) > 0
    )

    # # ***************************************************************************
    # # Test for RuntimeError Heudiconv doesn't allow overwrite
    # # ***************************************************************************

    run_heudiconv_cmd = shlex.split(
        f"{project} {subject} {xnat_bids_root} --session-suffix {session_suffix}"
    )
    print("Running run_heudiconv application:")
    r = runner.invoke(heudi_app, run_heudiconv_cmd)
    print(r.stdout)

    assert r.exit_code == 1

    # # ***************************************************************************
    # # Test overwrite is working
    # # ***************************************************************************

    run_heudiconv_cmd = shlex.split(
        f"{project} {subject} {xnat_bids_root} --session-suffix {session_suffix} --overwrite"
    )
    print("Running run_heudiconv application:")
    r = runner.invoke(heudi_app, run_heudiconv_cmd)
    print(r.stdout)

    assert r.exit_code == 0
