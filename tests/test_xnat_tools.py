from xnat_tools import __version__
import subprocess
import os
import shutil
import shlex
from dotenv import load_dotenv
load_dotenv()

def test_version():
    assert __version__ == '0.1.1'


def test_xnat2bids():

    xnat_user = "testuser"
    xnat_password  = os.getenv('XNAT_PASSWORD')
    session = "XNAT2_E00007"
    bids_root_dir = "./tests/xnat2bids"

    if os.path.exists(bids_root_dir):
        shutil.rmtree(bids_root_dir, ignore_errors=True)
    
    os.mkdir(bids_root_dir)

    xnat2bids_cmd = f"xnat2bids --user {xnat_user} --password {xnat_password} --session {session} \
                      --bids_root_dir {bids_root_dir} --seqlist 1 2 3 6 --skiplist 2 3"


    xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)
    
    subprocess.run(xnat2bids_split_cmd)

    bids_bold_run_path = "tests/xnat2bids/ashenhav/study-1222/bids/sub-test/ses-xnat2e00007/func"

    bids_bold_file = "sub-test_ses-xnat2e00007_task-RDMmotion_run-01_echo-1_bold"

    assert os.path.exists(bids_bold_run_path + "/" + bids_bold_file + ".json")
    assert os.path.exists(bids_bold_run_path + "/" + bids_bold_file + ".nii.gz")

    #cleanup output -- for debugging coment this out
    shutil.rmtree(bids_root_dir, ignore_errors=True)
