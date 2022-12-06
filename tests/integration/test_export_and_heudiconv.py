import glob
import os
import shlex
import shutil

import requests  # type: ignore
from dotenv import load_dotenv
from typer.testing import CliRunner

from xnat_tools.dicom_export import app as export_app
from xnat_tools.dicom_export import dicom_export
from xnat_tools.run_heudiconv import app as heudi_app
from xnat_tools.xnat_utils import get

from .test_xnat2bids import series_idx

load_dotenv()
runner = CliRunner()


def test_dicom_export():
    """Integration test for xnat-dicom-export"""
    xnat_user = os.environ.get("XNAT_USER", "")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    project = os.environ.get("XNAT_PROJECT", "bnc_demodat")
    subject = os.environ.get("XNAT_SUBJECT", "005")
    session = os.environ.get("XNAT_SESSION", "XNAT_E00114")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "-1")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)

    os.mkdir(bids_root_dir)

    # ***************************************************************************
    # Test for successful execution
    # Here we call the function directly. Note, that at the moment, when calling
    # the function, the default values are not correct.
    # See https://github.com/tiangolo/typer/issues/106
    # ***************************************************************************

    p, s, ss = dicom_export(
        session,
        bids_root_dir,
        user=xnat_user,
        password=xnat_pass,
        host="https://xnat.bnc.brown.edu",
        session_suffix=session_suffix,
        bidsmap_file="",
        includeseq=[9],
        skipseq=[],
        log_id="pytest",
        verbose=0,
        overwrite=False,
    )

    assert p == project
    assert s == subject
    assert ss == "session1"

    filepath = glob.glob(f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{ss}")[0]

    assert len(glob.glob(f"{filepath}/*/*.IMA")) > 0 or len(glob.glob(f"{filepath}/*/*.dcm")) > 0
    subdirs = [f.path for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 1
    for d in subdirs:
        for f in os.listdir(d):
            idx = series_idx(f)
            assert idx == "9"

    # ***************************************************************************
    # Test that default overwrite flag is NOT wiping the xnat-export directory
    # Here we test using typer's CLIRunner
    # ***************************************************************************

    cmd = f"{session} {bids_root_dir} -u {xnat_user} -p {xnat_pass} -i 7 -v"

    split_cmd = shlex.split(cmd)

    r = runner.invoke(export_app, split_cmd)
    print(r.stdout)

    filepath = glob.glob(f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{ss}")[0]
    subdirs = [f.path for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 2

    for d in subdirs:
        for f in os.listdir(d):
            idx = series_idx(f)
            assert idx in ["7", "9"]

    # # ***************************************************************************
    # # Test that overwrite flag is wiping the xnat-export directory
    # # ***************************************************************************

    cmd = f"{session} {bids_root_dir} -u {xnat_user} -p {xnat_pass} -v -i 7 --overwrite"

    split_cmd = shlex.split(cmd)

    r = runner.invoke(export_app, split_cmd)
    print(r.stdout)

    filepath = glob.glob(f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{ss}")[0]
    subdirs = [f.path for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 1


def test_heudiconv():
    """Integration test for running the run-heudiconv
    executable on the output of xnat-dicom-export"""
    project = os.environ.get("XNAT_PROJECT", "bnc_demodat")
    subject = os.environ.get("XNAT_SUBJECT", "005")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "SESSION1")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")

    # ***************************************************************************
    # Test for successful execution
    # ***************************************************************************
    cmd = f"{project} {subject} {bids_root_dir} --session-suffix {session_suffix}"

    split_cmd = shlex.split(cmd)

    r = runner.invoke(heudi_app, split_cmd)
    print(r.stdout)

    filepath = glob.glob(f"tests/xnat2bids/*/study-*/bids/sub-*/ses-{session_suffix}")[0]
    assert r.exit_code == 0

    assert (
        len(glob.glob(f"{filepath}/*/*.json")) > 0 or len(glob.glob(f"{filepath}/*/*.nii.gz")) > 0
    )

    # # ***************************************************************************
    # # Test for RuntimeError Heudiconv doesn't allow overwrite
    # # ***************************************************************************
    cmd = f"{project} {subject} {bids_root_dir} --session-suffix {session_suffix}"

    split_cmd = shlex.split(cmd)
    r = runner.invoke(heudi_app, split_cmd)
    print(r.stdout)

    assert r.exit_code == 1

    # # ***************************************************************************
    # # Test overwrite is working
    # # ***************************************************************************
    cmd = f"{project} {subject} {bids_root_dir} --session-suffix {session_suffix} --overwrite"

    split_cmd = shlex.split(cmd)
    r = runner.invoke(heudi_app, split_cmd)
    print(r.stdout)
    assert r.exit_code == 0

    # cleanup output -- for debugging comment this out
    shutil.rmtree(bids_root_dir, ignore_errors=True)


def test_unauthorized_user_exception_handling():
    """Test unauthorized user HTTPError response"""
    host = "https://xnat.bnc.brown.edu"
    session = "XNAT_E00114"
    url = f"{host}/data/experiments/{session}"

    user = "bad_user"
    password = "bad_password"

    connection = requests.Session()
    connection.verify = True
    connection.auth = (user, password)

    try:
        get(
            connection,
            url,
            params={"format": "json", "handler": "values", "columns": "project,subject_ID"},
        )
    except (requests.HTTPError) as e:
        assert e.response.status_code == 401


def test_xnat_reachable_exception_handling():
    """Test unauthorized user HTTPError response"""
    host = "https://xnat.bnc.brown.edu"
    session = "XNAT_BADPROJECT"
    url = f"{host}/data/experiments/{session}"

    user = os.environ.get("XNAT_USER", "")
    password = os.environ.get("XNAT_PASS", "")

    connection = requests.Session()
    connection.verify = True
    connection.auth = (user, password)

    try:
        get(
            connection,
            url,
            params={"format": "json", "handler": "values", "columns": "project,subject_ID"},
        )
    except (requests.HTTPError) as e:
        assert e.response.status_code == 404
