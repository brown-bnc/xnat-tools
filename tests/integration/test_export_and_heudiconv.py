import glob
import os
import shlex
import shutil

from dotenv import load_dotenv
from typer.testing import CliRunner

from xnat_tools.dicom_export import app as export_app
from xnat_tools.dicom_export import dicom_export
from xnat_tools.run_heudiconv import app as heudi_app

load_dotenv()
runner = CliRunner()


def test_dicom_export():
    """Integration test for xnat-dicom-export"""
    xnat_user = os.environ.get("XNAT_USER", "testuser")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    project = os.environ.get("XNAT_PROJECT", "")
    subject = os.environ.get("XNAT_SUBJECT", "")
    session = os.environ.get("XNAT_SESSION", "")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "01")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)

    os.mkdir(bids_root_dir)

    # ***************************************************************************
    # Test for succesfull execution
    # Here we call the function directly. Note, that at the moment, when calling
    # the fucntion, the default values are not correct.
    # See https://github.com/tiangolo/typer/issues/106
    # ***************************************************************************

    p, s, = dicom_export(
        session,
        bids_root_dir,
        user=xnat_user,
        password=xnat_pass,
        host="https://bnc.brown.edu/xnat",
        bidsmap_file="",
        session_suffix="01",
        includeseq=[9],
        skipseq=[],
        log_id="pytest",
        verbose=False,
        very_verbose=True,
        overwrite=False,
    )

    assert p == project
    assert s == subject

    filepath = glob.glob(
        f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]

    assert (
        len(glob.glob(f"{filepath}/*/*.IMA")) > 0
        or len(glob.glob(f"{filepath}/*/*.dcm")) > 0
    )
    subdirs = [f.path for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 1
    for d in subdirs:
        for f in os.listdir(d):
            dicom_sequence = int(f.split(".")[3])
            assert str(dicom_sequence) == "9"

    # ***************************************************************************
    # Test that default overwrite flag is NOT wiping the xnat-export directory
    # Here we test using typer's CLIRunner
    # ***************************************************************************

    cmd = f"{session} {bids_root_dir} -u {xnat_user} -p {xnat_pass} -i 8 -v"

    split_cmd = shlex.split(cmd)

    r = runner.invoke(export_app, split_cmd)
    print(r.stdout)

    filepath = glob.glob(
        f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]
    subdirs = [f.path for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 2

    for d in subdirs:
        for f in os.listdir(d):
            dicom_sequence = int(f.split(".")[3])
            assert str(dicom_sequence) in ["8", "9"]

    # ***************************************************************************
    # Test that overwrite flag is wiping the xnat-export directory
    # ***************************************************************************

    cmd = f"{session} {bids_root_dir} -u {xnat_user} -p {xnat_pass} -i 8 -v --overwrite"

    split_cmd = shlex.split(cmd)

    r = runner.invoke(export_app, split_cmd)
    print(r.stdout)

    filepath = glob.glob(
        f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]
    subdirs = [f.path for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 1

    for d in subdirs:
        for f in os.listdir(d):
            dicom_sequence = int(f.split(".")[3])
            assert str(dicom_sequence) == "8"


def test_heudiconv():
    """Integration test for running the run-heudiconv
    executable on the output of xnat-dicom-export"""
    project = os.environ.get("XNAT_PROJECT", "")
    subject = os.environ.get("XNAT_SUBJECT", "")
    session = os.environ.get("XNAT_SESSION", "")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "01")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")

    # ***************************************************************************
    # Test for succesfull execution
    # ***************************************************************************
    cmd = f"{project} {subject} {session} {bids_root_dir}"

    split_cmd = shlex.split(cmd)

    r = runner.invoke(heudi_app, split_cmd)
    print(r.stdout)

    filepath = glob.glob(f"tests/xnat2bids/*/study-*/bids/sub-*/ses-{session_suffix}")[0]
    assert r.exit_code == 0

    assert (
        len(glob.glob(f"{filepath}/*/*.json")) > 0
        or len(glob.glob(f"{filepath}/*/*.nii.gz")) > 0
    )

    # ***************************************************************************
    # Test for RuntimeError Heudiconv doesn't allow overwrite
    # ***************************************************************************
    cmd = f"{project} {subject} {session} {bids_root_dir}"

    split_cmd = shlex.split(cmd)
    r = runner.invoke(heudi_app, split_cmd)
    print(r.stdout)

    assert r.exit_code == 1

    # ***************************************************************************
    # Test overwrite is working
    # ***************************************************************************

    cmd = f"{project} {subject} {session} {bids_root_dir} --overwrite"

    split_cmd = shlex.split(cmd)
    r = runner.invoke(heudi_app, split_cmd)
    print(r.stdout)
    assert r.exit_code == 0

    # cleanup output -- for debugging coment this out
    shutil.rmtree(bids_root_dir, ignore_errors=True)
