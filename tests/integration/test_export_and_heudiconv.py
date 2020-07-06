import os
import glob
import subprocess
import shlex
import shutil
from dotenv import load_dotenv

load_dotenv()


def test_dicom_export():
    """Integration test for xnat-dicom-export"""
    xnat_user = os.environ.get("XNAT_USER", "testuser")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    session = os.environ.get("XNAT_SESSION", "")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "01")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)

    os.mkdir(bids_root_dir)

    # ***************************************************************************
    # Test for succesfull execution
    # ***************************************************************************

    cmd = f"xnat-dicom-export --user {xnat_user} --password {xnat_pass} \
                      --session {session} --session_suffix {session_suffix} \
                      --bids_root_dir {bids_root_dir} --seqlist 9 -vv"

    split_cmd = shlex.split(cmd)

    subprocess.run(split_cmd)

    filepath = glob.glob(
        f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]

    assert (
        len(glob.glob(f"{filepath}/*/*.IMA")) > 0
        or len(glob.glob(f"{filepath}/*/*.dcm")) > 0
    )
    subdirs = [f.name for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 1
    for d in subdirs:
        for f in os.listdir(d):
            dicom_sequence = int(f.split(".")[3])
            assert str(dicom_sequence) == 9

    # ***************************************************************************
    # Test that default overwrite flag is NOT wiping the xnat-export directory
    # ***************************************************************************

    cmd = f"xnat-dicom-export --user {xnat_user} --password {xnat_pass} \
                      --session {session} --session_suffix {session_suffix} \
                      --bids_root_dir {bids_root_dir} --seqlist 8 -vv "

    split_cmd = shlex.split(cmd)

    subprocess.run(split_cmd)

    filepath = glob.glob(
        f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]
    subdirs = [f.name for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 2

    for d in subdirs:
        for f in os.listdir(d):
            dicom_sequence = int(f.split(".")[3])
            assert str(dicom_sequence) in [8, 9]

    # ***************************************************************************
    # Test that overwrite flag is wiping the xnat-export directory
    # ***************************************************************************

    cmd = f"xnat-dicom-export --user {xnat_user} --password {xnat_pass} \
                      --session {session} --session_suffix {session_suffix} \
                      --bids_root_dir {bids_root_dir} --seqlist 8 -vv --overwrite"

    split_cmd = shlex.split(cmd)

    subprocess.run(split_cmd)

    filepath = glob.glob(
        f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]
    subdirs = [f.name for f in os.scandir(filepath) if f.is_dir()]

    assert len(subdirs) == 1

    for d in subdirs:
        for f in os.listdir(d):
            dicom_sequence = int(f.split(".")[3])
            assert str(dicom_sequence) == 8


def test_heudiconv():
    """Integration test for running xnat-heudiconv executable on the output of xnat-dicom-export """
    xnat_user = os.environ.get("XNAT_USER", "testuser")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    session = os.environ.get("XNAT_SESSION", "")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "01")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")

    # ***************************************************************************
    # Test for succesfull execution
    # ***************************************************************************

    cmd = f"xnat-heudiconv --user {xnat_user} --password {xnat_pass} \
            --session {session} --session_suffix {session_suffix} \
            --bids_root_dir {bids_root_dir}"

    split_cmd = shlex.split(cmd)

    subprocess.run(split_cmd)

    filepath = glob.glob(f"tests/xnat2bids/*/study-*/bids/sub-*/ses-{session_suffix}")[
        0
    ]

    subdirs = [f.name for f in os.scandir(filepath) if f.is_dir()]

    assert (
        len(glob.glob(f"{filepath}/*/*.json")) > 0
        or len(glob.glob(f"{filepath}/*/*.nii.gz")) > 0
    )

    # ***************************************************************************
    # Test for RuntimeError Heudiconv doesn't allow overwrite
    # ***************************************************************************
    cmd = f"xnat-heudiconv --user {xnat_user} --password {xnat_pass} \
            --session {session} --session_suffix {session_suffix} \
            --bids_root_dir {bids_root_dir}"

    split_cmd = shlex.split(cmd)
    p = subprocess.run(split_cmd)

    assert p.returncode == 1

    # ***************************************************************************
    # Test overwrite is working
    # ***************************************************************************

    cmd = f"xnat-heudiconv --user {xnat_user} --password {xnat_pass} \
            --session {session} --session_suffix {session_suffix} \
            --bids_root_dir {bids_root_dir} --overwrite"

    split_cmd = shlex.split(cmd)
    p = subprocess.run(split_cmd)
    assert p.returncode == 0

    # cleanup output -- for debugging coment this out
    shutil.rmtree(bids_root_dir, ignore_errors=True)
