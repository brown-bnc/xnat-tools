from xnat_tools import __version__
import subprocess
from subprocess import Popen, PIPE, STDOUT
import os
import glob
import shutil
import shlex
import json
from dotenv import load_dotenv
load_dotenv()

def test_xnat2bids():
    """Integration test for xnat2bids executable"""

    xnat_user = os.environ.get("XNAT_USER", "testuser")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    session = os.environ.get("XNAT_SESSION", "")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "01")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")
    
    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)

    os.mkdir(bids_root_dir)
    
    #***************************************************************************
    # Test for succesfull execution
    #***************************************************************************
    xnat2bids_cmd = f"xnat2bids --user {xnat_user} --password {xnat_pass} \
                      --session {session} --session_suffix {session_suffix} \
                      --bids_root_dir {bids_root_dir} --seqlist 1 2 3 6 --skiplist 2 3 -vv"


    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)
    
    subprocess.run(xnat2bids_split_cmd)

    filepath = f"tests/xnat2bids/*/study-*/bids/sub-*/ses-{session_suffix}"

    assert len(glob.glob(f"{filepath}/*/*.json")) > 0
    assert len(glob.glob(f"{filepath}/*/*.nii.gz")) > 0


    #***************************************************************************
    # Test for succesfull execution wit overwrite
    #***************************************************************************
    xnat2bids_cmd = f"xnat2bids --user {xnat_user} --password {xnat_pass} \
                      --session {session} --session_suffix {session_suffix} \
                      --bids_root_dir {bids_root_dir} --seqlist 1 2 3 6 --skiplist 2 3 -vv --overwrite"


    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)
    
    p = subprocess.run(xnat2bids_split_cmd)
    assert p.returncode == 0

    # cleanup output -- for debugging coment this out
    shutil.rmtree(bids_root_dir, ignore_errors=True)
