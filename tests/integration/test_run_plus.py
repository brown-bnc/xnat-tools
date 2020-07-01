from xnat_tools import __version__
import subprocess
import os
import shutil
import shlex
import json
from dotenv import load_dotenv
load_dotenv()

@pytest.mark.skip(reason="Another slow test")
def test_run_plus():
    """Integration test for sequence list"""
    xnat_user = os.environ.get("XNAT_USER", "testuser")
    xnat_pass = os.environ.get("XNAT_PASS", "")
    session = os.environ.get("XNAT_SESSION", "XNAT2_E00004")
    session_suffix = os.environ.get("XNAT_SESSION_SUFFIX", "01")
    bids_root_dir = os.environ.get("XNAT_BIDS_ROOT", "./tests/xnat2bids")
    sequence = [8, 12, 15]

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)
    
    os.mkdir(bids_root_dir)

    xnat2bids_cmd = f"xnat2bids --user {xnat_user} --password {xnat_pass} \
                      --session {session} --session_suffix {session_suffix} \
                      --bids_root_dir {bids_root_dir} --seqlist {' '.join(map(str, sequence))} -vv"


    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)
    
    cmd = subprocess.run(xnat2bids_split_cmd, check=True)

    xnat_export_path = f"tests/xnat2bids/shenhav/study-201226/xnat-export/sub-tcb2006/ses-{session_suffix}/"
    task_name = "func-bold_task-TSSblock_acq-2dot4mm-SMS4TR1200AP_run"

    assert os.path.isdir(os.path.join(os.getcwd(), xnat_export_path))
    for i in range(1, len(sequence) + 1):
        assert os.path.isdir(os.path.join(os.getcwd(), xnat_export_path, f"{task_name}-{i:02}"))

    #cleanup output -- for debugging coment this out
    shutil.rmtree(bids_root_dir, ignore_errors=True)
