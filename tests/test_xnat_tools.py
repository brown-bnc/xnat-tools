from xnat_tools import __version__
import subprocess
import os
import shutil
import shlex
from dotenv import load_dotenv
load_dotenv()

def test_version():
    assert __version__ == '0.1.1'


# def test_xnat2bids():
#     """Integration test for xnat2bids executable"""
#     xnat_user = "testuser"
#     xnat_password  = os.getenv('XNAT_PASSWORD')
#     session = "XNAT2_E00007"
#     session_suffix = "01"
#     bids_root_dir = "./tests/xnat2bids"

#     if os.path.exists(bids_root_dir):
#         shutil.rmtree(bids_root_dir, ignore_errors=True)
    
#     os.mkdir(bids_root_dir)

#     xnat2bids_cmd = f"xnat2bids --user {xnat_user} --password {xnat_password} \
#                       --session {session} --session_suffix {session_suffix} \
#                       --bids_root_dir {bids_root_dir} --seqlist 1 2 3 6 --skiplist 2 3"


#     xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)
    
#     subprocess.run(xnat2bids_split_cmd)

#     bids_bold_run_path = f"tests/xnat2bids/ashenhav/study-1222/bids/sub-test/ses-{session_suffix}/func"

#     bids_bold_file = f"sub-test_ses-{session_suffix}_task-RDMmotion_run-01_echo-1_bold"

#     assert os.path.exists(bids_bold_run_path + "/" + bids_bold_file + ".json")
#     assert os.path.exists(bids_bold_run_path + "/" + bids_bold_file + ".nii.gz")

#     #cleanup output -- for debugging coment this out
#     shutil.rmtree(bids_root_dir, ignore_errors=True)

def test_postprocessing():
    """Integration test for bids-postprocessing executable"""
    xnat_user = "testuser"
    xnat_password  = os.getenv('XNAT_PASSWORD')
    session = "XNAT2_E00017"
    session_suffix = "01"
    bids_root_dir = "./tests/xnat2bids"

    # if os.path.exists(bids_root_dir):
    #     shutil.rmtree(bids_root_dir, ignore_errors=True)
    
    # os.mkdir(bids_root_dir)

    # xnat2bids_cmd = f"xnat2bids --user {xnat_user} --password {xnat_password} \
    #                   --session {session} --session_suffix {session_suffix} \
    #                   --bids_root_dir {bids_root_dir} --seqlist 19 23 24"

    # xnat2bids_split_cmd = shlex.split(xnat2bids_cmd)
    
    # subprocess.run(xnat2bids_split_cmd)

    bids_dir = f"tests/xnat2bids/ashenhav/study-1222/bids/"

    postprocess_cmd = f"bids-postprocess --bids_experiment_dir {bids_dir} \
                         --session {session} --session_suffix {session_suffix} \
                         --subjlist 9011 9999 111 --skipsubj 9999 111"

    postprocess_split_cmd = shlex.split(postprocess_cmd)
    
    subprocess.run(postprocess_split_cmd)


