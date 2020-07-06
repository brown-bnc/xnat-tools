import subprocess
import os
import glob
import shutil
import shlex
from dotenv import load_dotenv

load_dotenv()


def test_xnat2bids():
    """Integration test for xnat2bids executable"""

    xnat_user = os.environ.get("XNAT_USER", "testuser")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    session = os.environ.get("XNAT_SESSION", "")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "01")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")
    seqlist = ["1", "2", "3", "6"]
    skiplist = ["2", "3"]

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)

    os.mkdir(bids_root_dir)

    xnat2bids_cmd = f"xnat2bids --user {xnat_user} --password {xnat_pass} \
                      --session {session} --session_suffix {session_suffix} \
                      --bids_root_dir {bids_root_dir} \
                      --seqlist {' '.join(seqlist)} --skiplist {' '.join(skiplist)} \
                      -vv"

    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)

    subprocess.run(xnat2bids_split_cmd)

    filepath = f"tests/xnat2bids/*/study-*/bids/sub-*/ses-{session_suffix}"

    # ***************************************************************************
    # Test for succesfull execution
    # ***************************************************************************
    assert len(glob.glob(f"{filepath}/*/*.json")) > 0
    assert len(glob.glob(f"{filepath}/*/*.nii.gz")) > 0

    # ***************************************************************************
    # Test for correctess of sequence number given by seqlist and skiplist
    # ***************************************************************************
    xnat_export_path = glob.glob(
        f"tests/xnat2bids/*/study-*/xnat-export/sub-*/ses-{session_suffix}"
    )[0]
    assert os.path.isdir(os.path.join(os.getcwd(), xnat_export_path))

    export_subdirs = [f.path for f in os.scandir(xnat_export_path) if f.is_dir()]

    for d in export_subdirs:
        for f in os.listdir(d):
            # print(f)
            dicom_sequence = int(f.split(".")[3])
            print("------- Dicom sequence:")
            # print(dicom_sequence)
            assert str(dicom_sequence) in seqlist
            assert str(dicom_sequence) not in skiplist


def test_xnat2bids_with_overwrite():
    """Integration test for xnat2bids executable with overwrite flag"""

    xnat_user = os.environ.get("XNAT_USER", "testuser")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    session = os.environ.get("XNAT_SESSION", "")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "01")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")
    seqlist = ["1", "2", "3", "6"]
    skiplist = ["2", "3"]

    # ***************************************************************************
    # Test for succesfull execution wit overwrite
    # ***************************************************************************
    xnat2bids_cmd = f"xnat2bids --user {xnat_user} --password {xnat_pass} \
                      --session {session} --session_suffix {session_suffix} \
                      --bids_root_dir {bids_root_dir} \
                      --seqlist {' '.join(seqlist)} --skiplist {' '.join(skiplist)} \
                      -vv --overwrite"

    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)

    p = subprocess.run(xnat2bids_split_cmd)
    assert p.returncode == 0

    # cleanup output -- for debugging coment this out
    shutil.rmtree(bids_root_dir, ignore_errors=True)
